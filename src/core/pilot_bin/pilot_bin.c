/*
 * pilot_bin.c -- PILOT.BIN parser/builder C extension
 *
 * PILOT.BIN is a flat binary file (no LZSS compression) containing pilot data.
 * File format:
 *   [0x00] uint32 LE count
 *   [0x04] PILOT[count]  (each sizeof(PILOT) bytes)
 *
 * Python API (via _pilot_bin.pyd):
 *   parse(data: bytearray | bytes, extra=None, trans=None) -> dict
 *   build(data: dict, extra=None, trans=None) -> bytearray
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "codec/codec.h"

/* ===================================================================
 * Constants
 * =================================================================== */

#define FNAME_SZ 0x25 /* 全名 37 字节 */
#define NNAME_SZ 0x0D /* 机师名 13 字节 */
#define SPIRIT_CNT 6  /* 精神个数 */
#define SKILL_CNT 3   /* 成长型技能条数 */

/* ===================================================================
 * 固定长度文本的默认掩码表
 * =================================================================== */

/* fname 默认掩码：前 10 字节因被第 0 条文本覆盖而不可考，假定为 0x00 */
static const unsigned char FNAME_DEFAULT_MASK[FNAME_SZ] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x67, 0x00, 0x58, 0xA5, 0xF7, 0xBF, 0x00, 0x00, 0x67, 0x00,
    0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08,
    0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0xBE,
};

static const unsigned char NNAME_DEFAULT_MASK[NNAME_SZ] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  /* 前 7 字节不可考，假定为 0x00 */
    0x22, 0x8F, 0xF8, 0xBF, 0x00, 0x00,
};

/* ===================================================================
 * 数据结构定义（pack(1) 确保与二进制布局一致）
 * =================================================================== */

#pragma pack(1)

typedef struct
{
    uint8_t sname; /* 技能映射码 */
    uint8_t l1;    /* Lv1 效果等级 */
    uint8_t l2;
    uint8_t l3;
    uint8_t l4;
    uint8_t l5;
    uint8_t l6;
    uint8_t l7;
    uint8_t l8;
    uint8_t l9;
} SKILL;

typedef struct
{
    uint16_t code;           /* 0x00 代码 */
    uint16_t series : 10;    /* 0x02 换乘系（低 10 位） */
    uint16_t unknown1 : 6;   /* 0x02 高 6 位 */
    char fname[FNAME_SZ];    /* 0x04 全名 */
    char nname[NNAME_SZ];    /* 0x29 机师名 */
    uint8_t cqb;             /* 0x36 格闘 */
    uint8_t rng;             /* 0x37 射撃 */
    uint8_t evd;             /* 0x38 回避 */
    uint8_t hit;             /* 0x39 命中 */
    uint8_t rxn;             /* 0x3A 反応 */
    uint8_t skl;             /* 0x3B 技量 */
    uint8_t spi[SPIRIT_CNT]; /* 0x3C 精神列表 */
    uint8_t spl[SPIRIT_CNT]; /* 0x42 习得等级 */
    SKILL sklu[SKILL_CNT];   /* 0x48 成长型技能 */
    uint8_t sp;              /* 0x66 ＳＰ */
    uint8_t daction;         /* 0x67 ２回行动 */
    uint16_t skls;           /* 0x68 特殊技能 */
    uint8_t nature;          /* 0x6A 性格 */
    uint8_t fsg;             /* 0x6B 气力组 */
    uint8_t air;             /* 0x6C 空适应 */
    uint8_t grd;             /* 0x6D 陆适应 */
    uint8_t wtr;             /* 0x6E 海适应 */
    uint8_t spc;             /* 0x6F 宇适应 */
} PILOT;

#pragma pack()

_Static_assert(sizeof(SKILL) == 0x0A, "SKILL size mismatch");
_Static_assert(sizeof(PILOT) == 0x70, "PILOT size mismatch");

/* ===================================================================
 * Little-endian helpers
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
 * 第一层：原始文件 ↔ 中间态（PILOT.BIN 无压缩，直接 memcpy）
 * =================================================================== */

static PILOT *pilots_parse(const unsigned char *data, uint32_t count)
{
    size_t total = (size_t)count * sizeof(PILOT);
    PILOT *pilots = (PILOT *)malloc(total);
    if (!pilots)
        return NULL;
    memcpy(pilots, data, total);
    return pilots;
}

/* ===================================================================
 * Python API: parse
 *
 *   parse(data, extra=None, trans=None) -> dict
 *
 * 解析 PILOT.BIN，解码文本字段后返回 Python dict。
 * =================================================================== */

static PyObject *
pilot_bin_parse(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"data", "extra", "trans", NULL};
    Py_buffer view;
    PyObject *extra = Py_None;
    PyObject *trans = Py_None;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y*|OO", (char **)kwlist,
                                     &view, &extra, &trans))
        return NULL;

    if (view.len < 4)
    {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_ValueError,
                        "PILOT.BIN data too short (need at least 4 bytes)");
        return NULL;
    }

    uint32_t count = _read_le32((const unsigned char *)view.buf);

    size_t data_size = view.len - 4;
    size_t expected = (size_t)count * sizeof(PILOT);
    if (data_size != expected)
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_ValueError,
                     "PILOT.BIN data size mismatch: "
                     "count=%u -> %zu bytes, but data has %zu bytes",
                     (unsigned)count, expected, data_size);
        return NULL;
    }

    PILOT *pilots = pilots_parse(
        (const unsigned char *)view.buf + 4, count);
    PyBuffer_Release(&view);

    if (!pilots)
        return PyErr_NoMemory();

    PyObject *result = PyDict_New();
    if (!result)
    {
        free(pilots);
        return NULL;
    }

    PyDict_SetItemString(result, "name", PyUnicode_FromString("pilot"));
    PyDict_SetItemString(result, "count", PyLong_FromLong((long)count));

    PyObject *pilots_list = PyList_New((Py_ssize_t)count);
    if (!pilots_list)
    {
        Py_DECREF(result);
        free(pilots);
        return NULL;
    }
    PyDict_SetItemString(result, "pilots", pilots_list);
    Py_DECREF(pilots_list);

    for (uint32_t i = 0; i < count; i++)
    {
        PILOT *p = &pilots[i];
        PyObject *pd = PyDict_New();
        if (!pd)
        {
            Py_DECREF(result);
            free(pilots);
            return NULL;
        }

        /* fname — codec 解码为 str */
        {
            PyObject *decoded = codec_decode(p->fname, FNAME_SZ, extra, trans);
            if (decoded)
            {
                PyDict_SetItemString(pd, "fname", decoded);
                Py_DECREF(decoded);
            }
        }

        /* nname — codec 解码为 str */
        {
            PyObject *decoded = codec_decode(p->nname, NNAME_SZ, extra, trans);
            if (decoded)
            {
                PyDict_SetItemString(pd, "nname", decoded);
                Py_DECREF(decoded);
            }
        }

        /* 数值字段（struct 直访） */
        PyDict_SetItemString(pd, "code", PyLong_FromLong(p->code));
        PyDict_SetItemString(pd, "series", PyLong_FromLong(p->series));
        PyDict_SetItemString(pd, "unknown1", PyLong_FromLong(p->unknown1));
        PyDict_SetItemString(pd, "cqb", PyLong_FromLong(p->cqb));
        PyDict_SetItemString(pd, "rng", PyLong_FromLong(p->rng));
        PyDict_SetItemString(pd, "evd", PyLong_FromLong(p->evd));
        PyDict_SetItemString(pd, "hit", PyLong_FromLong(p->hit));
        PyDict_SetItemString(pd, "rxn", PyLong_FromLong(p->rxn));
        PyDict_SetItemString(pd, "skl", PyLong_FromLong(p->skl));
        PyDict_SetItemString(pd, "sp", PyLong_FromLong(p->sp));
        PyDict_SetItemString(pd, "daction", PyLong_FromLong(p->daction));
        PyDict_SetItemString(pd, "skls", PyLong_FromLong(p->skls));
        PyDict_SetItemString(pd, "nature", PyLong_FromLong(p->nature));
        PyDict_SetItemString(pd, "fsg", PyLong_FromLong(p->fsg));
        PyDict_SetItemString(pd, "air", PyLong_FromLong(p->air));
        PyDict_SetItemString(pd, "grd", PyLong_FromLong(p->grd));
        PyDict_SetItemString(pd, "wtr", PyLong_FromLong(p->wtr));
        PyDict_SetItemString(pd, "spc", PyLong_FromLong(p->spc));

        /* spi — 精神列表 */
        {
            PyObject *lst = PyList_New(SPIRIT_CNT);
            if (!lst)
            {
                Py_DECREF(pd);
                Py_DECREF(result);
                free(pilots);
                return NULL;
            }
            for (int j = 0; j < SPIRIT_CNT; j++)
                PyList_SetItem(lst, j, PyLong_FromLong(p->spi[j]));
            PyDict_SetItemString(pd, "spi", lst);
            Py_DECREF(lst);
        }

        /* spl — 习得等级 */
        {
            PyObject *lst = PyList_New(SPIRIT_CNT);
            if (!lst)
            {
                Py_DECREF(pd);
                Py_DECREF(result);
                free(pilots);
                return NULL;
            }
            for (int j = 0; j < SPIRIT_CNT; j++)
                PyList_SetItem(lst, j, PyLong_FromLong(p->spl[j]));
            PyDict_SetItemString(pd, "spl", lst);
            Py_DECREF(lst);
        }

        /* sklu — 成长型技能列表 */
        {
            PyObject *sklu_list = PyList_New(SKILL_CNT);
            if (!sklu_list)
            {
                Py_DECREF(pd);
                Py_DECREF(result);
                free(pilots);
                return NULL;
            }
            for (int j = 0; j < SKILL_CNT; j++)
            {
                SKILL *sk = &p->sklu[j];
                PyObject *sd = PyDict_New();
                if (!sd)
                {
                    Py_DECREF(sklu_list);
                    Py_DECREF(pd);
                    Py_DECREF(result);
                    free(pilots);
                    return NULL;
                }
                PyDict_SetItemString(sd, "sname", PyLong_FromLong(sk->sname));
                PyDict_SetItemString(sd, "l1", PyLong_FromLong(sk->l1));
                PyDict_SetItemString(sd, "l2", PyLong_FromLong(sk->l2));
                PyDict_SetItemString(sd, "l3", PyLong_FromLong(sk->l3));
                PyDict_SetItemString(sd, "l4", PyLong_FromLong(sk->l4));
                PyDict_SetItemString(sd, "l5", PyLong_FromLong(sk->l5));
                PyDict_SetItemString(sd, "l6", PyLong_FromLong(sk->l6));
                PyDict_SetItemString(sd, "l7", PyLong_FromLong(sk->l7));
                PyDict_SetItemString(sd, "l8", PyLong_FromLong(sk->l8));
                PyDict_SetItemString(sd, "l9", PyLong_FromLong(sk->l9));
                PyList_SetItem(sklu_list, j, sd);
            }
            PyDict_SetItemString(pd, "sklu", sklu_list);
            Py_DECREF(sklu_list);
        }

        PyList_SetItem(pilots_list, (Py_ssize_t)i, pd);
    }

    free(pilots);
    return result;
}

/* ===================================================================
 * Python API: build
 *
 *   build(data, extra=None, trans=None) -> bytearray
 *
 * 从 Python dict 重建 PILOT.BIN 二进制。
 * 文本字段为 str 时经 codec.encode 编码，为 bytes 时直接覆写。
 * =================================================================== */

static PyObject *
pilot_bin_build(PyObject *self, PyObject *args, PyObject *kwargs)
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
    uint32_t count = (uint32_t)PyLong_AsLong(py_count);

    PyObject *py_pilots = PyDict_GetItemString(py_dict, "pilots");
    if (!py_pilots || !PyList_Check(py_pilots))
    {
        PyErr_SetString(PyExc_KeyError, "Missing or invalid 'pilots'");
        return NULL;
    }
    if ((Py_ssize_t)count != PyList_Size(py_pilots))
    {
        PyErr_SetString(PyExc_ValueError,
                        "'pilots' list size does not match 'count'");
        return NULL;
    }

    /* 空列表 */
    if (count == 0)
    {
        unsigned char *empty = (unsigned char *)malloc(4);
        if (!empty)
            return PyErr_NoMemory();
        _write_le32(empty, 0);
        PyObject *result = PyByteArray_FromStringAndSize((char *)empty, 4);
        free(empty);
        return result;
    }

    PILOT *pbase = (PILOT *)calloc((size_t)count, sizeof(PILOT));
    if (!pbase)
        return PyErr_NoMemory();

    /* 初始化掩码残影 */
    unsigned char fname_mask[FNAME_SZ];
    memcpy(fname_mask, FNAME_DEFAULT_MASK, FNAME_SZ);
    unsigned char nname_mask[NNAME_SZ];
    memcpy(nname_mask, NNAME_DEFAULT_MASK, NNAME_SZ);

    for (uint32_t i = 0; i < count; i++)
    {
        PyObject *pp = PyList_GetItem(py_pilots, (Py_ssize_t)i);
        if (!pp || !PyDict_Check(pp))
        {
            free(pbase);
            PyErr_SetString(PyExc_TypeError, "Each pilot must be a dict");
            return NULL;
        }

        PILOT *p = &pbase[i];
        PyObject *pv;

        /* fname — 掩码残影（str→codec_encode / bytes→直接覆写） */
        pv = PyDict_GetItemString(pp, "fname");
        if (pv)
        {
            if (PyUnicode_Check(pv))
            {
                if (PyUnicode_GET_LENGTH(pv) == 0)
                {
                    memset(p->fname, 0, FNAME_SZ);
                    memset(fname_mask, 0, FNAME_SZ);
                }
                else
                {
                    PyObject *enc = codec_encode(pv, extra, trans);
                    if (!enc)
                    {
                        free(pbase);
                        PyErr_SetString(PyExc_RuntimeError, "Failed to encode fname");
                        return NULL;
                    }
                    _mask_overlay((unsigned char *)p->fname,
                                  PyBytes_AsString(enc),
                                  PyBytes_Size(enc),
                                  FNAME_SZ, fname_mask);
                    Py_DECREF(enc);
                }
            }
            else if (PyBytes_Check(pv))
            {
                _mask_overlay((unsigned char *)p->fname,
                              PyBytes_AsString(pv),
                              PyBytes_Size(pv),
                              FNAME_SZ, fname_mask);
            }
        }

        /* nname — 掩码残影 */
        pv = PyDict_GetItemString(pp, "nname");
        if (pv)
        {
            if (PyUnicode_Check(pv))
            {
                if (PyUnicode_GET_LENGTH(pv) == 0)
                {
                    memset(p->nname, 0, NNAME_SZ);
                    memset(nname_mask, 0, NNAME_SZ);
                }
                else
                {
                    PyObject *enc = codec_encode(pv, extra, trans);
                    if (!enc)
                    {
                        free(pbase);
                        PyErr_SetString(PyExc_RuntimeError, "Failed to encode nname");
                        return NULL;
                    }
                    _mask_overlay((unsigned char *)p->nname,
                                  PyBytes_AsString(enc),
                                  PyBytes_Size(enc),
                                  NNAME_SZ, nname_mask);
                    Py_DECREF(enc);
                }
            }
            else if (PyBytes_Check(pv))
            {
                _mask_overlay((unsigned char *)p->nname,
                              PyBytes_AsString(pv),
                              PyBytes_Size(pv),
                              NNAME_SZ, nname_mask);
            }
        }

        /* 数值字段 */
        pv = PyDict_GetItemString(pp, "code");
        if (pv)
            p->code = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "series");
        if (pv)
            p->series = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "unknown1");
        if (pv)
            p->unknown1 = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "cqb");
        if (pv)
            p->cqb = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "rng");
        if (pv)
            p->rng = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "evd");
        if (pv)
            p->evd = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "hit");
        if (pv)
            p->hit = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "rxn");
        if (pv)
            p->rxn = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "skl");
        if (pv)
            p->skl = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "sp");
        if (pv)
            p->sp = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "daction");
        if (pv)
            p->daction = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "skls");
        if (pv)
            p->skls = (uint16_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "nature");
        if (pv)
            p->nature = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "fsg");
        if (pv)
            p->fsg = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "air");
        if (pv)
            p->air = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "grd");
        if (pv)
            p->grd = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "wtr");
        if (pv)
            p->wtr = (uint8_t)PyLong_AsLong(pv);
        pv = PyDict_GetItemString(pp, "spc");
        if (pv)
            p->spc = (uint8_t)PyLong_AsLong(pv);

        /* spi — 精神列表 */
        pv = PyDict_GetItemString(pp, "spi");
        if (pv && PyList_Check(pv))
        {
            int n = (int)PyList_Size(pv);
            if (n > SPIRIT_CNT)
                n = SPIRIT_CNT;
            for (int j = 0; j < n; j++)
            {
                PyObject *item = PyList_GetItem(pv, j);
                if (item && PyLong_Check(item))
                    p->spi[j] = (uint8_t)PyLong_AsLong(item);
            }
        }

        /* spl — 习得等级 */
        pv = PyDict_GetItemString(pp, "spl");
        if (pv && PyList_Check(pv))
        {
            int n = (int)PyList_Size(pv);
            if (n > SPIRIT_CNT)
                n = SPIRIT_CNT;
            for (int j = 0; j < n; j++)
            {
                PyObject *item = PyList_GetItem(pv, j);
                if (item && PyLong_Check(item))
                    p->spl[j] = (uint8_t)PyLong_AsLong(item);
            }
        }

        /* sklu — 成长型技能列表 */
        pv = PyDict_GetItemString(pp, "sklu");
        if (pv && PyList_Check(pv))
        {
            int n = (int)PyList_Size(pv);
            if (n > SKILL_CNT)
                n = SKILL_CNT;
            for (int j = 0; j < n; j++)
            {
                PyObject *sd = PyList_GetItem(pv, j);
                if (!sd || !PyDict_Check(sd))
                    continue;
                SKILL *sk = &p->sklu[j];
                PyObject *sv;

                sv = PyDict_GetItemString(sd, "sname");
                if (sv)
                    sk->sname = (uint8_t)PyLong_AsLong(sv);
                sv = PyDict_GetItemString(sd, "l1");
                if (sv)
                    sk->l1 = (uint8_t)PyLong_AsLong(sv);
                sv = PyDict_GetItemString(sd, "l2");
                if (sv)
                    sk->l2 = (uint8_t)PyLong_AsLong(sv);
                sv = PyDict_GetItemString(sd, "l3");
                if (sv)
                    sk->l3 = (uint8_t)PyLong_AsLong(sv);
                sv = PyDict_GetItemString(sd, "l4");
                if (sv)
                    sk->l4 = (uint8_t)PyLong_AsLong(sv);
                sv = PyDict_GetItemString(sd, "l5");
                if (sv)
                    sk->l5 = (uint8_t)PyLong_AsLong(sv);
                sv = PyDict_GetItemString(sd, "l6");
                if (sv)
                    sk->l6 = (uint8_t)PyLong_AsLong(sv);
                sv = PyDict_GetItemString(sd, "l7");
                if (sv)
                    sk->l7 = (uint8_t)PyLong_AsLong(sv);
                sv = PyDict_GetItemString(sd, "l8");
                if (sv)
                    sk->l8 = (uint8_t)PyLong_AsLong(sv);
                sv = PyDict_GetItemString(sd, "l9");
                if (sv)
                    sk->l9 = (uint8_t)PyLong_AsLong(sv);
            }
        }
    }

    /* 构建输出：4 字节头部 + 连续条目 */
    size_t out_len = 4 + (size_t)count * sizeof(PILOT);
    unsigned char *raw = (unsigned char *)malloc(out_len);
    if (!raw)
    {
        free(pbase);
        return PyErr_NoMemory();
    }

    _write_le32(raw, count);
    memcpy(raw + 4, pbase, (size_t)count * sizeof(PILOT));
    free(pbase);

    PyObject *result = PyByteArray_FromStringAndSize((char *)raw, (Py_ssize_t)out_len);
    free(raw);
    return result;
}

/* ===================================================================
 * 模块方法表
 * =================================================================== */

static PyMethodDef PilotBinMethods[] = {
    {"parse", (PyCFunction)pilot_bin_parse, METH_VARARGS | METH_KEYWORDS,
     "Parse PILOT.BIN data into a Python dict."},
    {"build", (PyCFunction)pilot_bin_build, METH_VARARGS | METH_KEYWORDS,
     "Build PILOT.BIN binary data from a Python dict."},
    {NULL, NULL, 0, NULL} /* sentinel */
};

/* ===================================================================
 * 模块定义
 * =================================================================== */

static struct PyModuleDef pilotbin_module = {
    PyModuleDef_HEAD_INIT,
    "_pilot_bin",
    "PILOT.BIN parser/builder",
    -1,
    PilotBinMethods,
};

/* ===================================================================
 * 模块入口
 * =================================================================== */

PyMODINIT_FUNC PyInit__pilot_bin(void)
{
    return PyModule_Create(&pilotbin_module);
}
