/*
 * robot_raf.c -- ROBOT.RAF parser/builder C extension
 *
 * ROBOT.RAF is an LZSS-compressed archive containing robot/weapon data.
 * See README.md for the full format specification.
 *
 * Python API (via _robot_raf.pyd):
 *   parse(data: bytearray) -> dict
 *   build(data: dict) -> bytearray
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "lzss/lzss.h"


/* ===================================================================
 * Constants
 * =================================================================== */

#define ROBOT_ENTRY_SIZE  0x2C4    /* sizeof(ROBOT) + 16 * sizeof(WEAPON) */
#define WEAPON_ENTRY_SIZE 0x28
#define WEAPON_COUNT      16


/* ===================================================================
 * Little-endian helpers
 * =================================================================== */

static uint16_t _read_le16(const unsigned char *p)
{
    return (uint16_t)(p[0]) | ((uint16_t)(p[1]) << 8);
}

static uint32_t _read_le32(const unsigned char *p)
{
    return ((uint32_t)p[0]) |
           ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) |
           ((uint32_t)p[3] << 24);
}

static void _write_le16(unsigned char *p, uint16_t v)
{
    p[0] = (unsigned char)(v & 0xff);
    p[1] = (unsigned char)((v >> 8) & 0xff);
}

static void _write_le32(unsigned char *p, uint32_t v)
{
    p[0] = (unsigned char)(v & 0xff);
    p[1] = (unsigned char)((v >> 8) & 0xff);
    p[2] = (unsigned char)((v >> 16) & 0xff);
    p[3] = (unsigned char)((v >> 24) & 0xff);
}

/* ===================================================================
 * 第一层：原始文件 <-> 中间态（逐条 LZSS 解压/压缩）
 * =================================================================== */

static unsigned char*
_entries_decompress(const unsigned char *raw, size_t raw_len,
                    int *out_count, size_t *out_entries_len)
{
    /* 检查最小长度：至少要有 count 字段 */
    if (!raw || raw_len < 4)
        return NULL;

    int count = (int)_read_le32(raw);
    if (count <= 0)
    {
        *out_count = 0;
        *out_entries_len = 0;
        return (unsigned char *)malloc(1);   /* 空有效负载，返回非 NULL 指针 */
    }

    size_t table_size = (size_t)count * 4;
    size_t data_start = 4 + table_size;

    /* 校验文件长度：需要 count 字段 + 完整指针表 */
    if (raw_len < data_start)
        return NULL;

    /* 读取指针表 */
    uint32_t *ptrs = (uint32_t *)malloc(table_size);
    if (!ptrs)
        return NULL;
    for (int i = 0; i < count; i++)
        ptrs[i] = _read_le32(raw + 4 + (size_t)i * 4);

    /* 逐块解压并拼接 */
    unsigned char *intermediate = NULL;
    size_t total = 0;
    int ok = 1;

    for (int i = 0; i < count; i++)
    {
        size_t block_off = data_start + ptrs[i];
        /* 每个块至少要有 8 字节头（size + zeros） */
        if (block_off + 8 > raw_len)
        {
            ok = 0;
            break;
        }

        uint32_t decomp_size = _read_le32(raw + block_off);

        /* LZSS 数据范围：从块头部算起到下一块开头（含 8 字节头，RAF 头 = LZSS 头） */
        size_t lzss_start = block_off;
        size_t lzss_size;
        if (i + 1 < count)
        {
            size_t next_off = data_start + ptrs[i + 1];
            if (next_off <= lzss_start)
            {
                ok = 0;
                break;
            }
            lzss_size = next_off - lzss_start;
        }
        else
        {
            lzss_size = raw_len - lzss_start;
        }

        /* 确保 LZSS 至少有自己的 8 字节头 */
        if (lzss_size < 8)
        {
            ok = 0;
            break;
        }

        uint8_t *decomp = NULL;
        uint32_t actual = 0;
        int ret = lzss_decompress(raw + lzss_start,
                                  (uint32_t)lzss_size,
                                  &decomp, &actual);
        if (ret != 0 || decomp == NULL || actual != decomp_size)
        {
            free(decomp);
            ok = 0;
            break;
        }

        /* 追加到中间态 */
        unsigned char *new_int = (unsigned char *)realloc(intermediate, total + actual);
        if (!new_int)
        {
            free(decomp);
            ok = 0;
            break;
        }
        intermediate = new_int;
        memcpy(intermediate + total, decomp, actual);
        total += actual;
        free(decomp);
    }

    free(ptrs);

    if (!ok)
    {
        free(intermediate);
        return NULL;
    }

    *out_count = count;
    *out_entries_len = total;
    return intermediate;
}


static unsigned char*
_entries_compress(const unsigned char *entries, size_t entries_len,
                  int count, size_t *out_len)
{
    if (count <= 0)
    {
        /* 空文件：只有 count=0 */
        unsigned char *buf = (unsigned char *)malloc(4);
        if (!buf) return NULL;
        _write_le32(buf, 0);
        *out_len = 4;
        return buf;
    }

    size_t entry_size = entries_len / (size_t)count;

    /* 计算最坏情况输出大小 */
    size_t per_entry_max = 16 + entry_size + entry_size / 8 + 1;   /* RAF 头 + LZSS 最坏 */
    size_t max_total = 4 + (size_t)count * 4 + (size_t)count * per_entry_max;

    unsigned char *out = (unsigned char *)calloc(max_total, 1);
    if (!out)
        return NULL;

    /* 写入记录数 */
    _write_le32(out, (uint32_t)count);

    size_t data_start = 4 + (size_t)count * 4;
    size_t cur = data_start;

    for (int i = 0; i < count; i++)
    {
        /* 写入指针：当前块相对数据区起始的偏移 */
        _write_le32(out + 4 + (size_t)i * 4, (uint32_t)(cur - data_start));

        /* LZSS 压缩单条记录 */
        uint8_t *comp = NULL;
        uint32_t comp_size = 0;
        int ret = lzss_compress(entries + (size_t)i * entry_size,
                                (uint32_t)entry_size,
                                &comp, &comp_size, 1);
        if (ret != 0 || !comp)
        {
            free(out);
            free(comp);
            return NULL;
        }

        /* 写入块头（RAF 头 = LZSS 头，不可重复写 LZSS 头） */
        _write_le32(out + cur, (uint32_t)entry_size);
        /* 4 字节 zeros 已在 calloc 时清零，跳过 */

        /* 只复制 LZSS 流（跳过 comp 的前 8 字节头，因 RAF 头已充当该角色） */
        memcpy(out + cur + 8, comp + 8, comp_size - 8);

        cur += comp_size;   /* 块总大小 = 8(RAF头) + (comp_size-8)(流) = comp_size */
        free(comp);
    }

    /* 裁剪到实际大小 */
    unsigned char *trimmed = (unsigned char *)realloc(out, cur);
    if (trimmed)
        out = trimmed;

    *out_len = cur;
    return out;
}


/* ===================================================================
 * 第二层辅助：析构 WEAPON 二进制 → Python dict
 * =================================================================== */

static PyObject*
_destruct_weapon(const unsigned char *entry)
{
    PyObject *d = PyDict_New();
    if (!d) return NULL;

    /* 0x00: code(4) | newtype(2) | aura(2) */
    {
        unsigned char b = entry[0];
        PyDict_SetItemString(d, "code",    PyLong_FromLong(b & 0x0F));
        PyDict_SetItemString(d, "newtype", PyLong_FromLong((b >> 4) & 0x03));
        PyDict_SetItemString(d, "aura",    PyLong_FromLong((b >> 6) & 0x03));
    }

    /* 0x01: morale */
    PyDict_SetItemString(d, "morale", PyLong_FromLong(entry[1]));

    /* 0x02: custom(2) | rngs(2) | rngl(4) */
    {
        unsigned char b = entry[2];
        PyDict_SetItemString(d, "custom", PyLong_FromLong(b & 0x03));
        PyDict_SetItemString(d, "rngs",   PyLong_FromLong((b >> 2) & 0x03));
        PyDict_SetItemString(d, "rngl",   PyLong_FromLong((b >> 4) & 0x0F));
    }

    /* 0x03: mcls(2) | radius(3) | unknown1(3) */
    {
        unsigned char b = entry[3];
        PyDict_SetItemString(d, "mcls",     PyLong_FromLong(b & 0x03));
        PyDict_SetItemString(d, "radius",   PyLong_FromLong((b >> 2) & 0x07));
        PyDict_SetItemString(d, "unknown1", PyLong_FromLong((b >> 5) & 0x07));
    }

    /* 0x04-0x05: damage */
    PyDict_SetItemString(d, "damage", PyLong_FromLong(_read_le16(entry + 4)));

    /* 0x06: class(1) | attr(7) */
    {
        unsigned char b = entry[6];
        PyDict_SetItemString(d, "class", PyLong_FromLong(b & 0x01));
        PyDict_SetItemString(d, "attr",  PyLong_FromLong((b >> 1) & 0x7F));
    }

    /* 0x07: unknown2(4) | bonus(4) */
    {
        unsigned char b = entry[7];
        PyDict_SetItemString(d, "unknown2", PyLong_FromLong(b & 0x0F));
        PyDict_SetItemString(d, "bonus",    PyLong_FromLong((b >> 4) & 0x0F));
    }

    /* 0x08-0x1C: wname (21 字节原始数据，后续接入 codec) */
    {
        PyObject *wname = PyBytes_FromStringAndSize((const char *)entry + 0x08, 0x15);
        if (wname)
            PyDict_SetItemString(d, "wname", wname);
        Py_XDECREF(wname);
    }

    /* 0x1D: mrng */
    PyDict_SetItemString(d, "mrng", PyLong_FromLong(entry[0x1D]));

    /* 0x1E: mshow */
    PyDict_SetItemString(d, "mshow", PyLong_FromLong(entry[0x1E]));

    /* 0x1F: encost */
    PyDict_SetItemString(d, "encost", PyLong_FromLong(entry[0x1F]));

    /* 0x20: hitrate (INT8) */
    PyDict_SetItemString(d, "hitrate", PyLong_FromLong((int)(int8_t)entry[0x20]));

    /* 0x21: crt (INT8) */
    PyDict_SetItemString(d, "crt", PyLong_FromLong((int)(int8_t)entry[0x21]));

    /* 0x22: ammod */
    PyDict_SetItemString(d, "ammod", PyLong_FromLong(entry[0x22]));

    /* 0x23: ammom */
    PyDict_SetItemString(d, "ammom", PyLong_FromLong(entry[0x23]));

    /* 0x24-0x27: 四项适应 */
    PyDict_SetItemString(d, "air", PyLong_FromLong(entry[0x24]));
    PyDict_SetItemString(d, "grd", PyLong_FromLong(entry[0x25]));
    PyDict_SetItemString(d, "wtr", PyLong_FromLong(entry[0x26]));
    PyDict_SetItemString(d, "spc", PyLong_FromLong(entry[0x27]));

    return d;
}


/* ===================================================================
 * Python API: parse
 *
 *   parse(data: bytearray | bytes) -> dict
 *
 * 解压 ROBOT.RAF 并返回 Python dict：
 *   {"name": "robot", "count": N, "robots": [{...}, ...]}
 * =================================================================== */

static PyObject*
robot_raf_parse(PyObject *self, PyObject *args)
{
    Py_buffer view;
    if (!PyArg_ParseTuple(args, "y*", &view))
        return NULL;

    int count;
    size_t entries_len;
    unsigned char *intermediate = _entries_decompress(
        (const unsigned char *)view.buf, view.len,
        &count, &entries_len);
    PyBuffer_Release(&view);

    if (!intermediate)
    {
        PyErr_SetString(PyExc_RuntimeError,
                        "Failed to decompress ROBOT.RAF data");
        return NULL;
    }

    size_t entry_size = ROBOT_ENTRY_SIZE;

    /* 合理性检查：中间态大小应与 count × 条目大小一致 */
    if ((size_t)count * entry_size != entries_len)
    {
        free(intermediate);
        PyErr_SetString(PyExc_RuntimeError,
                        "Decompressed data size mismatch "
                        "(expected count * ROBOT_ENTRY_SIZE)");
        return NULL;
    }

    /* 构建顶层 dict */
    PyObject *result = PyDict_New();
    if (!result) { free(intermediate); return NULL; }

    {
        PyObject *v = PyUnicode_FromString("robot");
        if (v) { PyDict_SetItemString(result, "name", v); Py_DECREF(v); }
    }
    {
        PyObject *v = PyLong_FromLong(count);
        if (v) { PyDict_SetItemString(result, "count", v); Py_DECREF(v); }
    }

    PyObject *robots_list = PyList_New(count);
    if (!robots_list) { Py_DECREF(result); free(intermediate); return NULL; }
    PyDict_SetItemString(result, "robots", robots_list);
    Py_DECREF(robots_list);  /* result 持有引用 */

    for (int i = 0; i < count; i++)
    {
        const unsigned char *entry = intermediate + (size_t)i * entry_size;
        PyObject *rd = PyDict_New();
        if (!rd) { Py_DECREF(result); free(intermediate); return NULL; }

        /* 0x00-0x19: rname */
        {
            PyObject *v = PyBytes_FromStringAndSize((const char *)entry, 0x1A);
            if (v) { PyDict_SetItemString(rd, "rname", v); Py_DECREF(v); }
        }

        /* 0x1A-0x1B: code */
        PyDict_SetItemString(rd, "code", PyLong_FromLong(_read_le16(entry + 0x1A)));

        /* 0x1C: type(4) | unknown1(4) */
        {
            unsigned char b = entry[0x1C];
            PyDict_SetItemString(rd, "type",     PyLong_FromLong(b & 0x0F));
            PyDict_SetItemString(rd, "unknown1", PyLong_FromLong((b >> 4) & 0x0F));
        }

        /* 0x1D: move */
        PyDict_SetItemString(rd, "move", PyLong_FromLong(entry[0x1D]));

        /* 0x1E-0x1F: hp */
        PyDict_SetItemString(rd, "hp", PyLong_FromLong(_read_le16(entry + 0x1E)));

        /* 0x20-0x21: en */
        PyDict_SetItemString(rd, "en", PyLong_FromLong(_read_le16(entry + 0x20)));

        /* 0x22-0x23: mobility */
        PyDict_SetItemString(rd, "mobility", PyLong_FromLong(_read_le16(entry + 0x22)));

        /* 0x24-0x25: armor */
        PyDict_SetItemString(rd, "armor", PyLong_FromLong(_read_le16(entry + 0x24)));

        /* 0x26-0x27: limit */
        PyDict_SetItemString(rd, "limit", PyLong_FromLong(_read_le16(entry + 0x26)));

        /* 0x28: size */
        PyDict_SetItemString(rd, "size", PyLong_FromLong(entry[0x28]));

        /* 0x29: slot */
        PyDict_SetItemString(rd, "slot", PyLong_FromLong(entry[0x29]));

        /* 0x2A-0x2B: series(10) | unknown2(6) */
        {
            uint16_t w = _read_le16(entry + 0x2A);
            PyDict_SetItemString(rd, "series",   PyLong_FromLong(w & 0x03FF));
            PyDict_SetItemString(rd, "unknown2", PyLong_FromLong((w >> 10) & 0x003F));
        }

        /* 0x2C-0x2F: abi(31) | unknown3(1) */
        {
            uint32_t dw = _read_le32(entry + 0x2C);
            PyDict_SetItemString(rd, "abi",      PyLong_FromLong(dw & 0x7FFFFFFF));
            PyDict_SetItemString(rd, "unknown3", PyLong_FromLong((dw >> 31) & 0x01));
        }

        /* 0x30-0x31: rep */
        PyDict_SetItemString(rd, "rep", PyLong_FromLong(_read_le16(entry + 0x30)));

        /* 0x32-0x33: cost */
        PyDict_SetItemString(rd, "cost", PyLong_FromLong(_read_le16(entry + 0x32)));

        /* 0x34: tgrp */
        PyDict_SetItemString(rd, "tgrp", PyLong_FromLong(entry[0x34]));

        /* 0x35: tsn */
        PyDict_SetItemString(rd, "tsn", PyLong_FromLong(entry[0x35]));

        /* 0x36: cgrp */
        PyDict_SetItemString(rd, "cgrp", PyLong_FromLong(entry[0x36]));

        /* 0x37: csn */
        PyDict_SetItemString(rd, "csn", PyLong_FromLong(entry[0x37]));

        /* 0x38-0x39: core */
        PyDict_SetItemString(rd, "core", PyLong_FromLong(_read_le16(entry + 0x38)));

        /* 0x3A: count（合体数） */
        PyDict_SetItemString(rd, "count", PyLong_FromLong(entry[0x3A]));

        /* 0x3B: option */
        PyDict_SetItemString(rd, "option", PyLong_FromLong(entry[0x3B]));

        /* 0x3C: bgm */
        PyDict_SetItemString(rd, "bgm", PyLong_FromLong(entry[0x3C]));

        /* 0x3D-0x3F: unknown4/5/6 */
        PyDict_SetItemString(rd, "unknown4", PyLong_FromLong(entry[0x3D]));
        PyDict_SetItemString(rd, "unknown5", PyLong_FromLong(entry[0x3E]));
        PyDict_SetItemString(rd, "unknown6", PyLong_FromLong(entry[0x3F]));

        /* 0x40-0x43: 四项适应 */
        PyDict_SetItemString(rd, "air", PyLong_FromLong(entry[0x40]));
        PyDict_SetItemString(rd, "grd", PyLong_FromLong(entry[0x41]));
        PyDict_SetItemString(rd, "wtr", PyLong_FromLong(entry[0x42]));
        PyDict_SetItemString(rd, "spc", PyLong_FromLong(entry[0x43]));

        /* 0x44 ~ 0x2C3: weapons[16] */
        {
            PyObject *wlist = PyList_New(WEAPON_COUNT);
            if (!wlist) { Py_DECREF(rd); Py_DECREF(result); free(intermediate); return NULL; }
            for (int j = 0; j < WEAPON_COUNT; j++)
            {
                PyObject *wd = _destruct_weapon(entry + 0x44 + (size_t)j * WEAPON_ENTRY_SIZE);
                if (!wd) { Py_DECREF(wlist); Py_DECREF(rd); Py_DECREF(result); free(intermediate); return NULL; }
                PyList_SetItem(wlist, j, wd);   /* 窃取引用 */
            }
            PyDict_SetItemString(rd, "weapons", wlist);
            Py_DECREF(wlist);
        }

        PyList_SetItem(robots_list, i, rd);     /* 窃取引用 */
    }

    free(intermediate);
    return result;
}


/* ===================================================================
 * Python API: build
 *
 *   build(data: dict) -> bytearray
 *
 * 从 Python dict 重建 ROBOT.RAF 二进制数据。
 * =================================================================== */

static PyObject*
robot_raf_build(PyObject *self, PyObject *args)
{
    PyObject *py_dict;
    if (!PyArg_ParseTuple(args, "O!", &PyDict_Type, &py_dict))
        return NULL;

    /* 提取 count */
    PyObject *py_count = PyDict_GetItemString(py_dict, "count");
    if (!py_count || !PyLong_Check(py_count))
    {
        PyErr_SetString(PyExc_KeyError, "Missing or invalid 'count'");
        return NULL;
    }
    int count = (int)PyLong_AsLong(py_count);

    /* 提取 robots 列表 */
    PyObject *py_robots = PyDict_GetItemString(py_dict, "robots");
    if (!py_robots || !PyList_Check(py_robots))
    {
        PyErr_SetString(PyExc_KeyError, "Missing or invalid 'robots'");
        return NULL;
    }
    if ((int)PyList_Size(py_robots) != count)
    {
        PyErr_SetString(PyExc_ValueError,
                        "'robots' list size does not match 'count'");
        return NULL;
    }

    if (count <= 0)
    {
        /* 空文件 */
        size_t out_len;
        unsigned char *raw = _entries_compress(NULL, 0, 0, &out_len);
        if (!raw)
        {
            PyErr_SetString(PyExc_RuntimeError, "Compression failed");
            return NULL;
        }
        PyObject *result = PyByteArray_FromStringAndSize((char *)raw, (Py_ssize_t)out_len);
        free(raw);
        return result;
    }

    /* 构建中间态 */
    size_t entry_size = ROBOT_ENTRY_SIZE;
    unsigned char *intermediate = (unsigned char *)calloc((size_t)count, entry_size);
    if (!intermediate)
        return PyErr_NoMemory();

    for (int i = 0; i < count; i++)
    {
        PyObject *pr = PyList_GetItem(py_robots, i);
        if (!pr || !PyDict_Check(pr))
        {
            free(intermediate);
            PyErr_SetString(PyExc_TypeError, "Each robot must be a dict");
            return NULL;
        }

        unsigned char *entry = intermediate + (size_t)i * entry_size;
        PyObject *pv;

        /* rname */
        pv = PyDict_GetItemString(pr, "rname");
        if (pv)
        {
            if (PyBytes_Check(pv))
            {
                Py_ssize_t n = PyBytes_Size(pv);
                if (n > 0x1A) n = 0x1A;
                memcpy(entry, PyBytes_AsString(pv), (size_t)n);
            }
            else if (PyByteArray_Check(pv))
            {
                Py_ssize_t n = PyByteArray_Size(pv);
                if (n > 0x1A) n = 0x1A;
                memcpy(entry, PyByteArray_AsString(pv), (size_t)n);
            }
        }

        /* code */
        pv = PyDict_GetItemString(pr, "code");
        if (pv) _write_le16(entry + 0x1A, (uint16_t)PyLong_AsLong(pv));

        /* type + unknown1 */
        {
            unsigned char b = 0;
            pv = PyDict_GetItemString(pr, "type");
            if (pv) b |= (PyLong_AsLong(pv) & 0x0F) << 0;
            pv = PyDict_GetItemString(pr, "unknown1");
            if (pv) b |= (PyLong_AsLong(pv) & 0x0F) << 4;
            entry[0x1C] = b;
        }

        /* move */
        pv = PyDict_GetItemString(pr, "move");
        if (pv) entry[0x1D] = (unsigned char)PyLong_AsLong(pv);

        /* hp */
        pv = PyDict_GetItemString(pr, "hp");
        if (pv) _write_le16(entry + 0x1E, (uint16_t)PyLong_AsLong(pv));

        /* en */
        pv = PyDict_GetItemString(pr, "en");
        if (pv) _write_le16(entry + 0x20, (uint16_t)PyLong_AsLong(pv));

        /* mobility */
        pv = PyDict_GetItemString(pr, "mobility");
        if (pv) _write_le16(entry + 0x22, (uint16_t)PyLong_AsLong(pv));

        /* armor */
        pv = PyDict_GetItemString(pr, "armor");
        if (pv) _write_le16(entry + 0x24, (uint16_t)PyLong_AsLong(pv));

        /* limit */
        pv = PyDict_GetItemString(pr, "limit");
        if (pv) _write_le16(entry + 0x26, (uint16_t)PyLong_AsLong(pv));

        /* size */
        pv = PyDict_GetItemString(pr, "size");
        if (pv) entry[0x28] = (unsigned char)PyLong_AsLong(pv);

        /* slot */
        pv = PyDict_GetItemString(pr, "slot");
        if (pv) entry[0x29] = (unsigned char)PyLong_AsLong(pv);

        /* series + unknown2 */
        {
            uint16_t w = 0;
            pv = PyDict_GetItemString(pr, "series");
            if (pv) w |= (PyLong_AsLong(pv) & 0x03FF) << 0;
            pv = PyDict_GetItemString(pr, "unknown2");
            if (pv) w |= (PyLong_AsLong(pv) & 0x003F) << 10;
            _write_le16(entry + 0x2A, w);
        }

        /* abi + unknown3 */
        {
            uint32_t dw = 0;
            pv = PyDict_GetItemString(pr, "abi");
            if (pv) dw |= (PyLong_AsLong(pv) & 0x7FFFFFFF) << 0;
            pv = PyDict_GetItemString(pr, "unknown3");
            if (pv) dw |= (PyLong_AsLong(pv) & 0x01) << 31;
            _write_le32(entry + 0x2C, dw);
        }

        /* rep */
        pv = PyDict_GetItemString(pr, "rep");
        if (pv) _write_le16(entry + 0x30, (uint16_t)PyLong_AsLong(pv));

        /* cost */
        pv = PyDict_GetItemString(pr, "cost");
        if (pv) _write_le16(entry + 0x32, (uint16_t)PyLong_AsLong(pv));

        /* tgrp */
        pv = PyDict_GetItemString(pr, "tgrp");
        if (pv) entry[0x34] = (unsigned char)PyLong_AsLong(pv);

        /* tsn */
        pv = PyDict_GetItemString(pr, "tsn");
        if (pv) entry[0x35] = (unsigned char)PyLong_AsLong(pv);

        /* cgrp */
        pv = PyDict_GetItemString(pr, "cgrp");
        if (pv) entry[0x36] = (unsigned char)PyLong_AsLong(pv);

        /* csn */
        pv = PyDict_GetItemString(pr, "csn");
        if (pv) entry[0x37] = (unsigned char)PyLong_AsLong(pv);

        /* core */
        pv = PyDict_GetItemString(pr, "core");
        if (pv) _write_le16(entry + 0x38, (uint16_t)PyLong_AsLong(pv));

        /* count（合体数） */
        pv = PyDict_GetItemString(pr, "count");
        if (pv) entry[0x3A] = (unsigned char)PyLong_AsLong(pv);

        /* option */
        pv = PyDict_GetItemString(pr, "option");
        if (pv) entry[0x3B] = (unsigned char)PyLong_AsLong(pv);

        /* bgm */
        pv = PyDict_GetItemString(pr, "bgm");
        if (pv) entry[0x3C] = (unsigned char)PyLong_AsLong(pv);

        /* unknown4/5/6 */
        pv = PyDict_GetItemString(pr, "unknown4");
        if (pv) entry[0x3D] = (unsigned char)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "unknown5");
        if (pv) entry[0x3E] = (unsigned char)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "unknown6");
        if (pv) entry[0x3F] = (unsigned char)PyLong_AsLong(pv);

        /* 四项适应 */
        pv = PyDict_GetItemString(pr, "air");
        if (pv) entry[0x40] = (unsigned char)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "grd");
        if (pv) entry[0x41] = (unsigned char)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "wtr");
        if (pv) entry[0x42] = (unsigned char)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "spc");
        if (pv) entry[0x43] = (unsigned char)PyLong_AsLong(pv);

        /* weapons */
        pv = PyDict_GetItemString(pr, "weapons");
        if (pv && PyList_Check(pv))
        {
            int nw = (int)PyList_Size(pv);
            if (nw > WEAPON_COUNT) nw = WEAPON_COUNT;
            for (int j = 0; j < nw; j++)
            {
                PyObject *pw = PyList_GetItem(pv, j);
                if (!pw || !PyDict_Check(pw)) continue;
                unsigned char *we = entry + 0x44 + (size_t)j * WEAPON_ENTRY_SIZE;
                PyObject *wv;

                /* byte 0x00: code | newtype | aura */
                {
                    unsigned char b = 0;
                    wv = PyDict_GetItemString(pw, "code");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x0F) << 0;
                    wv = PyDict_GetItemString(pw, "newtype");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x03) << 4;
                    wv = PyDict_GetItemString(pw, "aura");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x03) << 6;
                    we[0] = b;
                }

                /* 0x01: morale */
                wv = PyDict_GetItemString(pw, "morale");
                if (wv) we[1] = (unsigned char)PyLong_AsLong(wv);

                /* 0x02: custom | rngs | rngl */
                {
                    unsigned char b = 0;
                    wv = PyDict_GetItemString(pw, "custom");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x03) << 0;
                    wv = PyDict_GetItemString(pw, "rngs");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x03) << 2;
                    wv = PyDict_GetItemString(pw, "rngl");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x0F) << 4;
                    we[2] = b;
                }

                /* 0x03: mcls | radius | unknown1 */
                {
                    unsigned char b = 0;
                    wv = PyDict_GetItemString(pw, "mcls");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x03) << 0;
                    wv = PyDict_GetItemString(pw, "radius");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x07) << 2;
                    wv = PyDict_GetItemString(pw, "unknown1");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x07) << 5;
                    we[3] = b;
                }

                /* 0x04-0x05: damage */
                wv = PyDict_GetItemString(pw, "damage");
                if (wv) _write_le16(we + 4, (uint16_t)PyLong_AsLong(wv));

                /* 0x06: class | attr */
                {
                    unsigned char b = 0;
                    wv = PyDict_GetItemString(pw, "class");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x01) << 0;
                    wv = PyDict_GetItemString(pw, "attr");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x7F) << 1;
                    we[6] = b;
                }

                /* 0x07: unknown2 | bonus */
                {
                    unsigned char b = 0;
                    wv = PyDict_GetItemString(pw, "unknown2");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x0F) << 0;
                    wv = PyDict_GetItemString(pw, "bonus");
                    if (wv) b |= (PyLong_AsLong(wv) & 0x0F) << 4;
                    we[7] = b;
                }

                /* 0x08-0x1C: wname */
                wv = PyDict_GetItemString(pw, "wname");
                if (wv)
                {
                    const char *src = NULL;
                    Py_ssize_t n = 0;
                    if (PyBytes_Check(wv)) {
                        src = PyBytes_AsString(wv);
                        n = PyBytes_Size(wv);
                    } else if (PyByteArray_Check(wv)) {
                        src = PyByteArray_AsString(wv);
                        n = PyByteArray_Size(wv);
                    }
                    if (src) {
                        if (n > 0x15) n = 0x15;
                        memcpy(we + 8, src, (size_t)n);
                    }
                }

                /* 0x1D: mrng */
                wv = PyDict_GetItemString(pw, "mrng");
                if (wv) we[0x1D] = (unsigned char)PyLong_AsLong(wv);

                /* 0x1E: mshow */
                wv = PyDict_GetItemString(pw, "mshow");
                if (wv) we[0x1E] = (unsigned char)PyLong_AsLong(wv);

                /* 0x1F: encost */
                wv = PyDict_GetItemString(pw, "encost");
                if (wv) we[0x1F] = (unsigned char)PyLong_AsLong(wv);

                /* 0x20: hitrate */
                wv = PyDict_GetItemString(pw, "hitrate");
                if (wv) we[0x20] = (unsigned char)(int8_t)PyLong_AsLong(wv);

                /* 0x21: crt */
                wv = PyDict_GetItemString(pw, "crt");
                if (wv) we[0x21] = (unsigned char)(int8_t)PyLong_AsLong(wv);

                /* 0x22: ammod */
                wv = PyDict_GetItemString(pw, "ammod");
                if (wv) we[0x22] = (unsigned char)PyLong_AsLong(wv);

                /* 0x23: ammom */
                wv = PyDict_GetItemString(pw, "ammom");
                if (wv) we[0x23] = (unsigned char)PyLong_AsLong(wv);

                /* 0x24-0x27: 适应 */
                wv = PyDict_GetItemString(pw, "air");
                if (wv) we[0x24] = (unsigned char)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "grd");
                if (wv) we[0x25] = (unsigned char)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "wtr");
                if (wv) we[0x26] = (unsigned char)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "spc");
                if (wv) we[0x27] = (unsigned char)PyLong_AsLong(wv);
            }
        }
    }

    /* 压缩为 RAF 格式 */
    size_t out_len;
    unsigned char *raw_out = _entries_compress(intermediate,
                                                (size_t)count * entry_size,
                                                count, &out_len);
    free(intermediate);

    if (!raw_out)
    {
        PyErr_SetString(PyExc_RuntimeError,
                        "Failed to compress ROBOT.RAF data");
        return NULL;
    }

    PyObject *result = PyByteArray_FromStringAndSize((char *)raw_out,
                                                      (Py_ssize_t)out_len);
    free(raw_out);
    return result;
}


/* ===================================================================
 * Module registration
 * =================================================================== */

static PyMethodDef RobotRAFMethods[] = {
    {"parse", robot_raf_parse, METH_VARARGS,
     "parse(data) -> dict\n\n"
     "Decompress and parse ROBOT.RAF data into a Python dict.\n"
     "Accepts bytes or bytearray."},
    {"build", robot_raf_build, METH_VARARGS,
     "build(data) -> bytearray\n\n"
     "Build ROBOT.RAF binary data from a Python dict.\n"
     "The dict must have the same structure as the one returned by parse()."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef robot_raf_module = {
    PyModuleDef_HEAD_INIT,
    "_robot_raf",
    "ROBOT.RAF parser/builder for Super Robot Wars Alpha ROM Editor.",
    -1,
    RobotRAFMethods
};

PyMODINIT_FUNC PyInit__robot_raf(void)
{
    return PyModule_Create(&robot_raf_module);
}
