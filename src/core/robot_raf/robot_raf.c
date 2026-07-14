/*
 * robot_raf.c -- ROBOT.RAF parser/builder C extension
 *
 * ROBOT.RAF is an LZSS-compressed archive containing robot/weapon data.
 * Uses packed structs with bitfields for binary layout readability.
 * See README.md for the full format specification.
 *
 * Python API (via _robot_raf.pyd):
 *   parse(data: bytearray | bytes) -> dict
 *   build(data: dict) -> bytearray
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "lzss/lzss.h"
#include "codec/codec.h"

/* ===================================================================
 * Constants
 * =================================================================== */

#define WEAPON_COUNT 16
#define WNAME_SIZE 0x15 /* 武器名 21 字节 */
#define RNAME_SIZE 0x1A /* 机体名 26 字节 */

/* ===================================================================
 * 数据结构定义（pack(1) 确保与二进制布局一致）
 * =================================================================== */

#pragma pack(1)

typedef struct
{
    uint8_t code : 4;            /* 0x00 武器代码 */
    uint8_t newtype : 2;         /* ニュータイプ等级 */
    uint8_t aura : 2;            /* オーラ等级 */
    uint8_t morale;              /* 0x01 必要气力 */
    uint8_t custom : 2;          /* 0x02 改造区分 */
    uint8_t rngs : 2;            /* 最小射程 */
    uint8_t rngl : 4;            /* 最大射程 */
    uint8_t mcls : 2;            /* 0x03 マップ武器类别 */
    uint8_t radius : 3;          /* マップ半径 */
    uint8_t unknown1 : 3;
    uint16_t damage;             /* 0x04 攻击力 */
    uint8_t wclass : 1;          /* 0x06 武器等级 */
    uint8_t attr : 7;            /* 属性 */
    uint8_t unknown2 : 4;        /* 0x07 */
    uint8_t bonus : 4;           /* 改造ボーナス */
    char wname[WNAME_SIZE];      /* 0x08 武器名 */
    uint8_t mrng;                /* 0x1D マップ射程 */
    uint8_t mshow;               /* 0x1E マップ演出 */
    uint8_t encost;              /* 0x1F EN 消费 */
    int8_t hitrate;              /* 0x20 命中 */
    int8_t crt;                  /* 0x21 CT */
    uint8_t ammod;               /* 0x22 初期弹数 */
    uint8_t ammom;               /* 0x23 最大弹数 */
    uint8_t air;                 /* 0x24 空适应 */
    uint8_t grd;                 /* 0x25 陆适应 */
    uint8_t wtr;                 /* 0x26 海适应 */
    uint8_t spc;                 /* 0x27 宇适应 */
} WEAPON;

typedef struct
{
    char rname[RNAME_SIZE];      /* 0x000 机体名 */
    uint16_t code;               /* 0x01A 代码 */
    uint8_t type : 4;            /* 0x01C 移动类型 */
    uint8_t unknown1 : 4;
    uint8_t move;                /* 0x01D 移动力 */
    uint16_t hp;                 /* 0x01E HP */
    uint16_t en;                 /* 0x020 EN */
    uint16_t mobility;           /* 0x022 运动性 */
    uint16_t armor;              /* 0x024 装甲 */
    uint16_t limit;              /* 0x026 限界 */
    uint8_t size;                /* 0x028 サイズ */
    uint8_t slot;                /* 0x029 チップ数 */
    uint16_t series : 10;        /* 0x02A 换乘系 */
    uint16_t unknown2 : 6;
    uint32_t abi : 31;           /* 0x02C 特性 */
    uint32_t unknown3 : 1;
    uint16_t rep;                /* 0x030 修理费 */
    uint16_t cost;               /* 0x032 资金 */
    uint8_t tgrp;                /* 0x034 变形组番号 */
    uint8_t tsn;                 /* 0x035 变形连续番号 */
    uint8_t cgrp;                /* 0x036 合体组番号 */
    uint8_t csn;                 /* 0x037 合体连续番号 */
    uint16_t core;               /* 0x038 コアロボ */
    uint8_t count;               /* 0x03A 合体数 */
    uint8_t option;              /* 0x03B 换装システム */
    uint8_t bgm;                 /* 0x03C BGM */
    uint8_t unknown4;            /* 0x03D */
    uint8_t unknown5;            /* 0x03E */
    uint8_t unknown6;            /* 0x03F */
    uint8_t air;                 /* 0x040 空适应 */
    uint8_t grd;                 /* 0x041 陆适应 */
    uint8_t wtr;                 /* 0x042 海适应 */
    uint8_t spc;                 /* 0x043 宇适应 */
    WEAPON weapons[WEAPON_COUNT]; /* 0x044 武器列表 */
} ROBOT;

#pragma pack()

_Static_assert(sizeof(ROBOT) == 0x2C4, "ROBOT struct size mismatch (expected 0x2C4)");
_Static_assert(sizeof(WEAPON) == 0x28, "WEAPON struct size mismatch (expected 0x28)");

/* ===================================================================
 * Little-endian helpers（仅 LZSS 层使用，struct 层用直访）
 * =================================================================== */

static uint32_t _read_le32(const unsigned char *p)
{
    return ((uint32_t)p[0]) |
           ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) |
           ((uint32_t)p[3] << 24);
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

static unsigned char *
_entries_decompress(const unsigned char *raw, size_t raw_len,
                    int *out_count, size_t *out_entries_len)
{
    if (!raw || raw_len < 4)
        return NULL;

    int count = (int)_read_le32(raw);
    if (count <= 0)
    {
        *out_count = 0;
        *out_entries_len = 0;
        return (unsigned char *)malloc(1);
    }

    size_t table_size = (size_t)count * 4;
    size_t data_start = 4 + table_size;

    if (raw_len < data_start)
        return NULL;

    uint32_t *ptrs = (uint32_t *)malloc(table_size);
    if (!ptrs)
        return NULL;
    for (int i = 0; i < count; i++)
        ptrs[i] = _read_le32(raw + 4 + (size_t)i * 4);

    unsigned char *intermediate = NULL;
    size_t total = 0;
    int ok = 1;

    for (int i = 0; i < count; i++)
    {
        size_t block_off = data_start + ptrs[i];
        if (block_off + 8 > raw_len)
        {
            ok = 0;
            break;
        }

        uint32_t decomp_size = _read_le32(raw + block_off);

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

static unsigned char *
_entries_compress(const unsigned char *entries, size_t entries_len,
                  int count, size_t *out_len)
{
    if (count <= 0)
    {
        unsigned char *buf = (unsigned char *)malloc(4);
        if (!buf)
            return NULL;
        _write_le32(buf, 0);
        *out_len = 4;
        return buf;
    }

    size_t entry_size = entries_len / (size_t)count;
    size_t per_entry_max = 16 + entry_size + entry_size / 8 + 1;
    size_t max_total = 4 + (size_t)count * 4 + (size_t)count * per_entry_max;

    unsigned char *out = (unsigned char *)calloc(max_total, 1);
    if (!out)
        return NULL;

    _write_le32(out, (uint32_t)count);

    size_t data_start = 4 + (size_t)count * 4;
    size_t cur = data_start;

    for (int i = 0; i < count; i++)
    {
        _write_le32(out + 4 + (size_t)i * 4, (uint32_t)(cur - data_start));

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

        _write_le32(out + cur, (uint32_t)entry_size);
        memcpy(out + cur + 8, comp + 8, comp_size - 8);
        cur += comp_size;
        free(comp);
    }

    unsigned char *trimmed = (unsigned char *)realloc(out, cur);
    if (trimmed)
        out = trimmed;

    *out_len = cur;
    return out;
}

/* ===================================================================
 * 固定长度文本的默认掩码表
 * =================================================================== */

static const unsigned char WNAME_DEFAULT_MASKS[WEAPON_COUNT][WNAME_SIZE] = {
    {0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
     0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20}, /* W00: 全 20 */
    {0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11,
     0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C}, /* W01: 08~1C */
    {0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,
     0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40, 0x61, 0x62, 0x63, 0x64}, /* W02: 30~40→61~64 */
    {0x58, 0x59, 0x5A, 0x5B, 0x5C, 0x5D, 0x5E, 0x5F, 0x60, 0x61,
     0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x6B, 0x6C}, /* W03: 58~6C */
    {0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
     0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20}, /* W04: 全 20 */
    {0xA8, 0xA9, 0xAA, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF, 0xB0, 0xB1,
     0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7, 0xB8, 0xB9, 0xBA, 0xBB, 0xBC}, /* W05: A8~BC */
    {0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9,
     0xDA, 0xDB, 0xDC, 0xDD, 0xDE, 0xDF, 0x20, 0x20, 0x20, 0x20, 0x20}, /* W06: D0~DF→20×5 */
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},    /* W07~W15: 全 00 */
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
};

static const unsigned char RNAME_DEFAULT_MASK[RNAME_SIZE] = {
    0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
    0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xAB, 0xAC, 0xAD,
};

/* ===================================================================
 * 辅助：在掩码上覆写文本（残影核心）
 *
 * 从 src 中取首个 0x00 前的文本，覆写到 mask 上。
 * src 为空/全 00 时输出全 00，mask 也重置。
 * =================================================================== */

static void _mask_overlay(unsigned char *dst, const char *src,
                          Py_ssize_t src_len, int buf_size,
                          unsigned char *running_mask)
{
    if (!src || src_len <= 0)
    {
        /* 无数据：全 00 */
        memset(dst, 0, (size_t)buf_size);
        memset(running_mask, 0, (size_t)buf_size);
        return;
    }

    /* 检查是否全空 */
    int all_zero = 1;
    for (Py_ssize_t i = 0; i < buf_size && i < src_len; i++)
    {
        if (src[i] != 0)
        {
            all_zero = 0;
            break;
        }
    }

    if (all_zero)
    {
        memset(dst, 0, (size_t)buf_size);
        memset(running_mask, 0, (size_t)buf_size);
        return;
    }

    /* 取 mask 作底 */
    memcpy(dst, running_mask, (size_t)buf_size);

    /* 找文本长度 */
    int text_len = 0;
    while (text_len < buf_size && text_len < (int)src_len && src[text_len] != 0)
        text_len++;

    if (text_len > 0)
        memcpy(dst, src, (size_t)text_len);

    /* 00 终结 */
    if (text_len < buf_size)
        dst[text_len] = 0;

    /* 更新残影 */
    memcpy(running_mask, dst, (size_t)buf_size);
}

/* ===================================================================
 * Python API: parse
 *
 *   parse(data, extra=None, trans=None) -> dict
 *
 * 解压 ROBOT.RAF，解码文本字段后返回 Python dict。
 * =================================================================== */

static PyObject *
robot_raf_parse(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"data", "extra", "trans", NULL};
    Py_buffer view;
    PyObject *extra = Py_None;
    PyObject *trans = Py_None;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y*|OO", (char **)kwlist,
                                     &view, &extra, &trans))
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

    if ((size_t)count * sizeof(ROBOT) != entries_len)
    {
        free(intermediate);
        PyErr_SetString(PyExc_RuntimeError,
                        "Decompressed data size mismatch");
        return NULL;
    }

    PyObject *result = PyDict_New();
    if (!result)
    {
        free(intermediate);
        return NULL;
    }

    PyDict_SetItemString(result, "name", PyUnicode_FromString("robot"));
    PyDict_SetItemString(result, "count", PyLong_FromLong(count));

    PyObject *robots_list = PyList_New(count);
    if (!robots_list)
    {
        Py_DECREF(result);
        free(intermediate);
        return NULL;
    }
    PyDict_SetItemString(result, "robots", robots_list);
    Py_DECREF(robots_list);

    ROBOT *robase = (ROBOT *)intermediate;

    for (int i = 0; i < count; i++)
    {
        ROBOT *r = &robase[i];
        PyObject *rd = PyDict_New();
        if (!rd)
        {
            Py_DECREF(result);
            free(intermediate);
            return NULL;
        }

        /* rname — codec 解码为 str */
        {
            PyObject *decoded = codec_decode(r->rname, RNAME_SIZE, extra, trans);
            if (decoded)
            {
                PyDict_SetItemString(rd, "rname", decoded);
                Py_DECREF(decoded);
            }
        }

        /* 数值字段（struct 直访） */
        PyDict_SetItemString(rd, "code", PyLong_FromLong(r->code));
        PyDict_SetItemString(rd, "type", PyLong_FromLong(r->type));
        PyDict_SetItemString(rd, "unknown1", PyLong_FromLong(r->unknown1));
        PyDict_SetItemString(rd, "move", PyLong_FromLong(r->move));
        PyDict_SetItemString(rd, "hp", PyLong_FromLong(r->hp));
        PyDict_SetItemString(rd, "en", PyLong_FromLong(r->en));
        PyDict_SetItemString(rd, "mobility", PyLong_FromLong(r->mobility));
        PyDict_SetItemString(rd, "armor", PyLong_FromLong(r->armor));
        PyDict_SetItemString(rd, "limit", PyLong_FromLong(r->limit));
        PyDict_SetItemString(rd, "size", PyLong_FromLong(r->size));
        PyDict_SetItemString(rd, "slot", PyLong_FromLong(r->slot));
        PyDict_SetItemString(rd, "series", PyLong_FromLong(r->series));
        PyDict_SetItemString(rd, "unknown2", PyLong_FromLong(r->unknown2));
        PyDict_SetItemString(rd, "abi", PyLong_FromLong(r->abi));
        PyDict_SetItemString(rd, "unknown3", PyLong_FromLong(r->unknown3));
        PyDict_SetItemString(rd, "rep", PyLong_FromLong(r->rep));
        PyDict_SetItemString(rd, "cost", PyLong_FromLong(r->cost));
        PyDict_SetItemString(rd, "tgrp", PyLong_FromLong(r->tgrp));
        PyDict_SetItemString(rd, "tsn", PyLong_FromLong(r->tsn));
        PyDict_SetItemString(rd, "cgrp", PyLong_FromLong(r->cgrp));
        PyDict_SetItemString(rd, "csn", PyLong_FromLong(r->csn));
        PyDict_SetItemString(rd, "core", PyLong_FromLong(r->core));
        PyDict_SetItemString(rd, "count", PyLong_FromLong(r->count));
        PyDict_SetItemString(rd, "option", PyLong_FromLong(r->option));
        PyDict_SetItemString(rd, "bgm", PyLong_FromLong(r->bgm));
        PyDict_SetItemString(rd, "unknown4", PyLong_FromLong(r->unknown4));
        PyDict_SetItemString(rd, "unknown5", PyLong_FromLong(r->unknown5));
        PyDict_SetItemString(rd, "unknown6", PyLong_FromLong(r->unknown6));
        PyDict_SetItemString(rd, "air", PyLong_FromLong(r->air));
        PyDict_SetItemString(rd, "grd", PyLong_FromLong(r->grd));
        PyDict_SetItemString(rd, "wtr", PyLong_FromLong(r->wtr));
        PyDict_SetItemString(rd, "spc", PyLong_FromLong(r->spc));

        /* weapons */
        PyObject *wlist = PyList_New(WEAPON_COUNT);
        if (!wlist)
        {
            Py_DECREF(rd);
            Py_DECREF(result);
            free(intermediate);
            return NULL;
        }

        for (int j = 0; j < WEAPON_COUNT; j++)
        {
            WEAPON *w = &r->weapons[j];
            PyObject *wd = PyDict_New();
            if (!wd)
            {
                Py_DECREF(wlist);
                Py_DECREF(rd);
                Py_DECREF(result);
                free(intermediate);
                return NULL;
            }

            PyDict_SetItemString(wd, "code", PyLong_FromLong(w->code));
            PyDict_SetItemString(wd, "newtype", PyLong_FromLong(w->newtype));
            PyDict_SetItemString(wd, "aura", PyLong_FromLong(w->aura));
            PyDict_SetItemString(wd, "morale", PyLong_FromLong(w->morale));
            PyDict_SetItemString(wd, "custom", PyLong_FromLong(w->custom));
            PyDict_SetItemString(wd, "rngs", PyLong_FromLong(w->rngs));
            PyDict_SetItemString(wd, "rngl", PyLong_FromLong(w->rngl));
            PyDict_SetItemString(wd, "mcls", PyLong_FromLong(w->mcls));
            PyDict_SetItemString(wd, "radius", PyLong_FromLong(w->radius));
            PyDict_SetItemString(wd, "unknown1", PyLong_FromLong(w->unknown1));
            PyDict_SetItemString(wd, "damage", PyLong_FromLong(w->damage));
            PyDict_SetItemString(wd, "class", PyLong_FromLong(w->wclass));
            PyDict_SetItemString(wd, "attr", PyLong_FromLong(w->attr));
            PyDict_SetItemString(wd, "unknown2", PyLong_FromLong(w->unknown2));
            PyDict_SetItemString(wd, "bonus", PyLong_FromLong(w->bonus));

            /* wname — codec 解码为 str */
            {
                PyObject *decoded = codec_decode(w->wname, WNAME_SIZE, extra, trans);
                if (decoded)
                {
                    PyDict_SetItemString(wd, "wname", decoded);
                    Py_DECREF(decoded);
                }
            }

            PyDict_SetItemString(wd, "mrng", PyLong_FromLong(w->mrng));
            PyDict_SetItemString(wd, "mshow", PyLong_FromLong(w->mshow));
            PyDict_SetItemString(wd, "encost", PyLong_FromLong(w->encost));
            PyDict_SetItemString(wd, "hitrate", PyLong_FromLong(w->hitrate));
            PyDict_SetItemString(wd, "crt", PyLong_FromLong(w->crt));
            PyDict_SetItemString(wd, "ammod", PyLong_FromLong(w->ammod));
            PyDict_SetItemString(wd, "ammom", PyLong_FromLong(w->ammom));
            PyDict_SetItemString(wd, "air", PyLong_FromLong(w->air));
            PyDict_SetItemString(wd, "grd", PyLong_FromLong(w->grd));
            PyDict_SetItemString(wd, "wtr", PyLong_FromLong(w->wtr));
            PyDict_SetItemString(wd, "spc", PyLong_FromLong(w->spc));

            PyList_SetItem(wlist, j, wd);
        }
        PyDict_SetItemString(rd, "weapons", wlist);
        Py_DECREF(wlist);

        PyList_SetItem(robots_list, i, rd);
    }

    free(intermediate);
    return result;
}

/* ===================================================================
 * Python API: build
 *
 *   build(data, extra=None, trans=None) -> bytearray
 *
 * 从 Python dict 重建 ROBOT.RAF 二进制。
 * 文本字段为 str 时经 codec.encode 编码，为 bytes 时直接覆写到掩码。
 * 采用掩码残影写入。
 * =================================================================== */

static PyObject *
robot_raf_build(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"data", "extra", "trans", NULL};
    PyObject *py_dict;
    PyObject *extra = Py_None;
    PyObject *trans = Py_None;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!|OO", (char **)kwlist,
                                     &PyDict_Type, &py_dict, &extra, &trans))
        return NULL;

    PyObject *py_count = PyDict_GetItemString(py_dict, "count");
    if (!py_count || !PyLong_Check(py_count))
    {
        PyErr_SetString(PyExc_KeyError, "Missing or invalid 'count'");
        return NULL;
    }
    int count = (int)PyLong_AsLong(py_count);

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

    ROBOT *robase = (ROBOT *)calloc((size_t)count, sizeof(ROBOT));
    if (!robase)
        return PyErr_NoMemory();

    /* 初始化掩码残影 */
    unsigned char weapon_masks[WEAPON_COUNT][WNAME_SIZE];
    memcpy(weapon_masks, WNAME_DEFAULT_MASKS, sizeof(WNAME_DEFAULT_MASKS));
    unsigned char rname_mask[RNAME_SIZE];
    memcpy(rname_mask, RNAME_DEFAULT_MASK, RNAME_SIZE);

    for (int i = 0; i < count; i++)
    {
        PyObject *pr = PyList_GetItem(py_robots, i);
        if (!pr || !PyDict_Check(pr))
        {
            free(robase);
            PyErr_SetString(PyExc_TypeError, "Each robot must be a dict");
            return NULL;
        }

        ROBOT *r = &robase[i];
        PyObject *pv;

        /* rname — 掩码残影（str→codec_encode / bytes→直接覆写） */
        pv = PyDict_GetItemString(pr, "rname");
        if (pv)
        {
            if (PyUnicode_Check(pv))
            {
                if (PyUnicode_GET_LENGTH(pv) == 0)
                {
                    memset(r->rname, 0, RNAME_SIZE);
                    memset(rname_mask, 0, RNAME_SIZE);
                }
                else
                {
                    PyObject *enc = codec_encode(pv, extra, trans);
                    if (!enc)
                    {
                        free(robase);
                        PyErr_SetString(PyExc_RuntimeError, "Failed to encode rname");
                        return NULL;
                    }
                    _mask_overlay((unsigned char *)r->rname, PyBytes_AsString(enc), PyBytes_Size(enc), RNAME_SIZE, rname_mask);
                    Py_DECREF(enc);
                }
            }
            else
            {
                const char *src = NULL;
                Py_ssize_t src_len = 0;
                if (PyBytes_Check(pv))
                {
                    src = PyBytes_AsString(pv);
                    src_len = PyBytes_Size(pv);
                }
                else if (PyByteArray_Check(pv))
                {
                    src = PyByteArray_AsString(pv);
                    src_len = PyByteArray_Size(pv);
                }
                _mask_overlay((unsigned char *)r->rname, src, src_len, RNAME_SIZE, rname_mask);
            }
        }

        /* 数值字段 — struct 直访 */
        pv = PyDict_GetItemString(pr, "code");
        if (pv)
            r->code = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "type");
        if (pv)
            r->type = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "unknown1");
        if (pv)
            r->unknown1 = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "move");
        if (pv)
            r->move = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "hp");
        if (pv)
            r->hp = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "en");
        if (pv)
            r->en = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "mobility");
        if (pv)
            r->mobility = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "armor");
        if (pv)
            r->armor = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "limit");
        if (pv)
            r->limit = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "size");
        if (pv)
            r->size = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "slot");
        if (pv)
            r->slot = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "series");
        if (pv)
            r->series = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "unknown2");
        if (pv)
            r->unknown2 = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "abi");
        if (pv)
            r->abi = (uint32_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "unknown3");
        if (pv)
            r->unknown3 = (uint32_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "rep");
        if (pv)
            r->rep = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "cost");
        if (pv)
            r->cost = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "tgrp");
        if (pv)
            r->tgrp = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "tsn");
        if (pv)
            r->tsn = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "cgrp");
        if (pv)
            r->cgrp = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "csn");
        if (pv)
            r->csn = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "core");
        if (pv)
            r->core = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "count");
        if (pv)
            r->count = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "option");
        if (pv)
            r->option = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "bgm");
        if (pv)
            r->bgm = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "unknown4");
        if (pv)
            r->unknown4 = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "unknown5");
        if (pv)
            r->unknown5 = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "unknown6");
        if (pv)
            r->unknown6 = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "air");
        if (pv)
            r->air = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "grd");
        if (pv)
            r->grd = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "wtr");
        if (pv)
            r->wtr = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pr, "spc");
        if (pv)
            r->spc = (uint8_t)PyLong_AsLong(pv);

        /* weapons */
        pv = PyDict_GetItemString(pr, "weapons");
        if (pv && PyList_Check(pv))
        {
            int nw = (int)PyList_Size(pv);
            if (nw > WEAPON_COUNT)
                nw = WEAPON_COUNT;
            for (int j = 0; j < nw; j++)
            {
                PyObject *pw = PyList_GetItem(pv, j);
                if (!pw || !PyDict_Check(pw))
                    continue;
                WEAPON *w = &r->weapons[j];
                PyObject *wv;

                wv = PyDict_GetItemString(pw, "code");
                if (wv)
                    w->code = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "newtype");
                if (wv)
                    w->newtype = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "aura");
                if (wv)
                    w->aura = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "morale");
                if (wv)
                    w->morale = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "custom");
                if (wv)
                    w->custom = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "rngs");
                if (wv)
                    w->rngs = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "rngl");
                if (wv)
                    w->rngl = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "mcls");
                if (wv)
                    w->mcls = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "radius");
                if (wv)
                    w->radius = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "unknown1");
                if (wv)
                    w->unknown1 = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "damage");
                if (wv)
                    w->damage = (uint16_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "class");
                if (wv)
                    w->wclass = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "attr");
                if (wv)
                    w->attr = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "unknown2");
                if (wv)
                    w->unknown2 = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "bonus");
                if (wv)
                    w->bonus = (uint8_t)PyLong_AsLong(wv);

                /* wname — 掩码残影（str→codec_encode / bytes→直接覆写） */
                wv = PyDict_GetItemString(pw, "wname");
                if (wv)
                {
                    if (PyUnicode_Check(wv))
                    {
                        if (PyUnicode_GET_LENGTH(wv) == 0)
                        {
                            memset(w->wname, 0, WNAME_SIZE);
                            memset(weapon_masks[j], 0, WNAME_SIZE);
                        }
                        else
                        {
                            PyObject *enc = codec_encode(wv, extra, trans);
                            if (!enc)
                            {
                                free(robase);
                                PyErr_SetString(PyExc_RuntimeError, "Failed to encode wname");
                                return NULL;
                            }
                            _mask_overlay((unsigned char *)w->wname, PyBytes_AsString(enc), PyBytes_Size(enc), WNAME_SIZE, weapon_masks[j]);
                            Py_DECREF(enc);
                        }
                    }
                    else
                    {
                        const char *src = NULL;
                        Py_ssize_t src_len = 0;
                        if (PyBytes_Check(wv))
                        {
                            src = PyBytes_AsString(wv);
                            src_len = PyBytes_Size(wv);
                        }
                        else if (PyByteArray_Check(wv))
                        {
                            src = PyByteArray_AsString(wv);
                            src_len = PyByteArray_Size(wv);
                        }
                        _mask_overlay((unsigned char *)w->wname, src, src_len, WNAME_SIZE, weapon_masks[j]);
                    }
                }

                wv = PyDict_GetItemString(pw, "mrng");
                if (wv)
                    w->mrng = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "mshow");
                if (wv)
                    w->mshow = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "encost");
                if (wv)
                    w->encost = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "hitrate");
                if (wv)
                    w->hitrate = (int8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "crt");
                if (wv)
                    w->crt = (int8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "ammod");
                if (wv)
                    w->ammod = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "ammom");
                if (wv)
                    w->ammom = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "air");
                if (wv)
                    w->air = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "grd");
                if (wv)
                    w->grd = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "wtr");
                if (wv)
                    w->wtr = (uint8_t)PyLong_AsLong(wv);
                wv = PyDict_GetItemString(pw, "spc");
                if (wv)
                    w->spc = (uint8_t)PyLong_AsLong(wv);
            }
        }
    }

    /* 压缩为 RAF 格式 */
    size_t out_len;
    unsigned char *raw_out = _entries_compress((unsigned char *)robase,
                                               (size_t)count * sizeof(ROBOT),
                                               count, &out_len);
    free(robase);

    if (!raw_out)
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to compress ROBOT.RAF data");
        return NULL;
    }

    PyObject *result = PyByteArray_FromStringAndSize((char *)raw_out, (Py_ssize_t)out_len);
    free(raw_out);
    return result;
}

/* ===================================================================
 * Module registration
 * =================================================================== */

static PyMethodDef RobotRAFMethods[] = {
    {"parse", (PyCFunction)robot_raf_parse, METH_VARARGS | METH_KEYWORDS,
     "parse(data, extra=None, trans=None) -> dict\n\n"
     "Decompress and parse ROBOT.RAF data into a Python dict.\n"
     "Text fields (rname, wname) are decoded via codec.decode with\n"
     "optional extra/trans mappings."},
    {"build", (PyCFunction)robot_raf_build, METH_VARARGS | METH_KEYWORDS,
     "build(data, extra=None, trans=None) -> bytearray\n\n"
     "Build ROBOT.RAF binary data from a Python dict.\n"
     "Text fields can be str (encoded via codec.encode) or bytes.\n"
     "Uses mask residue for fixed-length text buffers."},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef robot_raf_module = {
    PyModuleDef_HEAD_INIT,
    "_robot_raf",
    "ROBOT.RAF parser/builder for Super Robot Wars Alpha ROM Editor.",
    -1,
    RobotRAFMethods};

PyMODINIT_FUNC PyInit__robot_raf(void)
{
    return PyModule_Create(&robot_raf_module);
}
