/*
 * dr_bin.c -- DR.BIN parser/builder C extension
 *
 * DR.BIN 是机体图鉴数据文件，包含 449 个 LZSS 压缩块：
 *   块 0 — 机体名册（448 × 0x30 字节记录）
 *   块 1~448 — 各机体详情
 *
 * 文件格式：
 *   0x0000~0x0707  指针表（450 × uint32 LE）
 *   0x0708~EOF      数据区（LZSS 压缩块，pack=4 对齐）
 *
 * Python API:
 *   parse(data: bytearray | bytes, extra=None, trans=None) -> dict
 *   build(data: dict, extra=None, trans=None) -> bytearray
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

/* 详情块字段偏移 */
#define DR_OFF_NAME         0x00   /* 机体名 */
#define DR_SLOT_NAME        0x30
#define DR_OFF_HEIGHT       0x30   /* 全高 */
#define DR_SLOT_HEIGHT      0x20
#define DR_OFF_WEIGHT       0x50   /* 重量 */
#define DR_SLOT_WEIGHT      0x20
#define DR_OFF_APPR         0x70   /* 出身作品 */
#define DR_SLOT_APPR        0x40
#define DR_OFF_FLAGS        0xB0   /* 4 字节 flags */
#define DR_SIZE_FLAGS       4
#define DR_OFF_DESC_START   0xB4   /* 描述文本起始偏移 */
#define DR_DESC_CELL_SIZE   0x30   /* 对齐倍数 */

/* 块 0 名册 */
#define DR_ROSTER_SLOT_SIZE 0x30

/* 指针表 */
#define DR_PTR_COUNT        450
#define DR_PTR_TABLE_SIZE   0x708

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
    p[0] = (unsigned char)(v & 0xFF);
    p[1] = (unsigned char)((v >> 8) & 0xFF);
    p[2] = (unsigned char)((v >> 16) & 0xFF);
    p[3] = (unsigned char)((v >> 24) & 0xFF);
}

/* ===================================================================
 * 解压/压缩单个 LZSS 块
 * =================================================================== */

static unsigned char *_decompress_block(
    const unsigned char *comp_data, size_t comp_size,
    size_t *out_decomp_size)
{
    uint8_t *raw = NULL;
    uint32_t raw_size = 0;

    int ret = lzss_decompress(comp_data, (uint32_t)comp_size, &raw, &raw_size);
    if (ret != 0 || !raw)
        return NULL;

    *out_decomp_size = (size_t)raw_size;
    return raw;
}

static unsigned char *_compress_block(
    const unsigned char *raw_data, size_t raw_size,
    size_t *out_comp_size)
{
    uint8_t *comp = NULL;
    uint32_t comp_size = 0;

    int ret = lzss_compress(raw_data, (uint32_t)raw_size, &comp, &comp_size, 4);
    if (ret != 0 || !comp)
        return NULL;

    *out_comp_size = (size_t)comp_size;
    return comp;
}

/* ===================================================================
 * 从固定偏移读取 00 截断文本 → Python str
 * =================================================================== */

static PyObject *_read_text_field(
    const unsigned char *buf, size_t buf_size,
    size_t offset, size_t max_len,
    PyObject *extra, PyObject *trans)
{
    if (offset >= buf_size)
        return PyUnicode_FromString("");

    size_t limit = offset + max_len;
    if (limit > buf_size)
        limit = buf_size;

    size_t len = limit - offset;
    return codec_decode((const char *)(buf + offset), len, extra, trans);
}

/* ===================================================================
 * 编码文本并写入缓冲区，末尾加 00
 *
 * 返回写入的字节数（含 00），出错返回 -1。
 * =================================================================== */

static Py_ssize_t _write_text_field(
    unsigned char *buf, size_t buf_size, size_t offset, size_t slot_size,
    PyObject *text, PyObject *extra, PyObject *trans)
{
    if (offset + slot_size > buf_size)
        return -1;

    PyObject *encoded = codec_encode(text, extra, trans);
    if (!encoded)
        return -1;

    Py_ssize_t text_len = PyBytes_Size(encoded);
    if (text_len < 0)
    {
        Py_DECREF(encoded);
        return -1;
    }

    if ((size_t)text_len >= slot_size)
        text_len = (Py_ssize_t)(slot_size - 1);

    char *enc_buf = PyBytes_AsString(encoded);
    if (!enc_buf)
    {
        Py_DECREF(encoded);
        return -1;
    }

    memcpy(buf + offset, enc_buf, (size_t)text_len);
    buf[offset + text_len] = 0x00;

    Py_DECREF(encoded);
    return text_len + 1;
}

/* ===================================================================
 * 解析描述文本
 *
 * 从 start_offset 开始扫描，00 00 为强制换行。
 * 所有行用 \n 拼接为一个字符串。
 * =================================================================== */

static PyObject *_parse_description(
    const unsigned char *buf, size_t buf_size, size_t start_offset,
    PyObject *extra, PyObject *trans)
{
    enum { MAX_LINES = 256 };
    char **lines = (char **)malloc((size_t)MAX_LINES * sizeof(char *));
    Py_ssize_t *line_lens = (Py_ssize_t *)malloc(
        (size_t)MAX_LINES * sizeof(Py_ssize_t));
    if (!lines || !line_lens)
    {
        free(lines);
        free(line_lens);
        return NULL;
    }

    Py_ssize_t line_count = 0;
    size_t pos = start_offset;

    while (pos < buf_size && line_count < MAX_LINES)
    {
        size_t null_pos = pos;
        while (null_pos < buf_size && buf[null_pos] != 0x00)
            null_pos++;

        size_t seg_len = null_pos - pos;

        if (seg_len > 0)
        {
            size_t cd_skip = 0;
            while (cd_skip < seg_len && buf[pos + cd_skip] == 0xCD)
                cd_skip++;

            if (cd_skip < seg_len)
            {
                PyObject *line_str = codec_decode(
                    (const char *)(buf + pos + cd_skip),
                    seg_len - cd_skip, extra, trans);
                if (!line_str)
                {
                    for (Py_ssize_t j = 0; j < line_count; j++)
                        free(lines[j]);
                    free(lines);
                    free(line_lens);
                    return NULL;
                }

                PyObject *utf8 = PyUnicode_AsUTF8String(line_str);
                Py_DECREF(line_str);
                if (!utf8)
                {
                    for (Py_ssize_t j = 0; j < line_count; j++)
                        free(lines[j]);
                    free(lines);
                    free(line_lens);
                    return NULL;
                }

                Py_ssize_t utf8_len = PyBytes_Size(utf8);
                lines[line_count] = (char *)malloc((size_t)utf8_len + 1);
                if (!lines[line_count])
                {
                    Py_DECREF(utf8);
                    for (Py_ssize_t j = 0; j < line_count; j++)
                        free(lines[j]);
                    free(lines);
                    free(line_lens);
                    return NULL;
                }
                memcpy(lines[line_count], PyBytes_AsString(utf8),
                       (size_t)utf8_len);
                lines[line_count][utf8_len] = '\0';
                line_lens[line_count] = utf8_len;
                Py_DECREF(utf8);
                line_count++;
            }
        }

        pos = null_pos + 1;

        if (pos < buf_size && buf[pos] == 0x00)
        {
            if (line_count > 0)
            {
                Py_ssize_t prev = line_count - 1;
                lines[prev] = (char *)realloc(lines[prev],
                                              (size_t)(line_lens[prev] + 2));
                if (lines[prev])
                {
                    lines[prev][line_lens[prev]] = '\n';
                    lines[prev][line_lens[prev] + 1] = '\0';
                    line_lens[prev]++;
                }
            }
            pos++;
        }
    }

    Py_ssize_t total = 0;
    for (Py_ssize_t j = 0; j < line_count; j++)
        total += line_lens[j];

    char *desc_buf = (char *)malloc((size_t)total + 1);
    if (!desc_buf)
    {
        for (Py_ssize_t j = 0; j < line_count; j++)
            free(lines[j]);
        free(lines);
        free(line_lens);
        return NULL;
    }

    char *p = desc_buf;
    for (Py_ssize_t j = 0; j < line_count; j++)
    {
        memcpy(p, lines[j], (size_t)line_lens[j]);
        p += line_lens[j];
        free(lines[j]);
    }
    *p = '\0';
    free(lines);
    free(line_lens);

    PyObject *result = PyUnicode_DecodeUTF8(desc_buf, total, NULL);
    free(desc_buf);

    /* 去掉末尾多余的 \n（原数据最后一行后只有 00 而非 00 00） */
    if (result)
    {
        Py_ssize_t rlen = PyUnicode_GET_LENGTH(result);
        if (rlen > 0)
        {
            Py_UCS4 last_char = PyUnicode_ReadChar(result, rlen - 1);
            if (last_char == (Py_UCS4)'\n')
            {
                PyObject *trimmed = PyUnicode_Substring(result, 0, rlen - 1);
                if (trimmed)
                {
                    Py_DECREF(result);
                    result = trimmed;
                }
            }
        }
    }

    return result;
}

/* ===================================================================
 * 解析单个机体详情块
 * =================================================================== */

static PyObject *_parse_robot(
    const unsigned char *decomp, size_t decomp_size,
    PyObject *extra, PyObject *trans)
{
    PyObject *robot_dict = PyDict_New();
    if (!robot_dict)
        return NULL;

    /* 机体名 @ 0x00 */
    {
        PyObject *v = _read_text_field(decomp, decomp_size,
                                        DR_OFF_NAME, DR_SLOT_NAME,
                                        extra, trans);
        if (!v) { Py_DECREF(robot_dict); return NULL; }
        PyDict_SetItemString(robot_dict, "name", v);
        Py_DECREF(v);
    }

    /* 全高 @ 0x30 */
    {
        PyObject *v = _read_text_field(decomp, decomp_size,
                                        DR_OFF_HEIGHT, DR_SLOT_HEIGHT,
                                        extra, trans);
        if (!v) { Py_DECREF(robot_dict); return NULL; }
        PyDict_SetItemString(robot_dict, "height", v);
        Py_DECREF(v);
    }

    /* 重量 @ 0x50 */
    {
        PyObject *v = _read_text_field(decomp, decomp_size,
                                        DR_OFF_WEIGHT, DR_SLOT_WEIGHT,
                                        extra, trans);
        if (!v) { Py_DECREF(robot_dict); return NULL; }
        PyDict_SetItemString(robot_dict, "weight", v);
        Py_DECREF(v);
    }

    /* 出身 @ 0x70 */
    {
        PyObject *v = _read_text_field(decomp, decomp_size,
                                        DR_OFF_APPR, DR_SLOT_APPR,
                                        extra, trans);
        if (!v) { Py_DECREF(robot_dict); return NULL; }
        PyDict_SetItemString(robot_dict, "appr", v);
        Py_DECREF(v);
    }

    /* flags @ 0xB0 */
    if (DR_OFF_FLAGS + DR_SIZE_FLAGS <= decomp_size)
    {
        uint32_t flags = _read_le32(decomp + DR_OFF_FLAGS);
        PyObject *v = PyLong_FromUnsignedLong(flags);
        if (!v) { Py_DECREF(robot_dict); return NULL; }
        PyDict_SetItemString(robot_dict, "flags", v);
        Py_DECREF(v);
    }

    /* 描述文本 @ 0xB4 */
    if (DR_OFF_DESC_START < decomp_size)
    {
        PyObject *desc = _parse_description(decomp, decomp_size,
                                             DR_OFF_DESC_START,
                                             extra, trans);
        if (!desc) { Py_DECREF(robot_dict); return NULL; }
        PyDict_SetItemString(robot_dict, "desc", desc);
        Py_DECREF(desc);
    }
    else
    {
        PyDict_SetItemString(robot_dict, "desc",
                             PyUnicode_FromString(""));
    }

    return robot_dict;
}

/* ===================================================================
 * 名册专用 extra：拷贝传入 extra 并添加 { "-": "ー" } 映射，
 * 保护条目（key==value）自然阻止 - 被转换，无需特殊处理
 * =================================================================== */

static PyObject *_make_roster_extra(PyObject *extra)
{
    PyObject *roster_extra;
    if (extra && extra != Py_None)
        roster_extra = PyDict_Copy(extra);
    else
        roster_extra = PyDict_New();
    if (!roster_extra) return NULL;

    PyObject *k = PyUnicode_FromString("-");
    PyObject *v = PyUnicode_FromString("ー");
    if (k && v) PyDict_SetItem(roster_extra, k, v);
    Py_XDECREF(k); Py_XDECREF(v);
    return roster_extra;
}

/* ===================================================================
 * 解析块 0（机体名册）→ Python list of str
 * =================================================================== */

static PyObject *_parse_roster(
    const unsigned char *data, size_t size,
    PyObject *extra, PyObject *trans)
{
    if (size < DR_ROSTER_SLOT_SIZE)
        return NULL;

    size_t count = size / DR_ROSTER_SLOT_SIZE;

    PyObject *roster_extra = _make_roster_extra(extra);
    if (!roster_extra)
        return NULL;

    PyObject *roster = PyList_New((Py_ssize_t)count);
    if (!roster)
    {
        Py_DECREF(roster_extra);
        return NULL;
    }

    for (size_t i = 0; i < count; i++)
    {
        size_t offset = i * DR_ROSTER_SLOT_SIZE;
        PyObject *name = _read_text_field(data, size, offset,
                                           DR_ROSTER_SLOT_SIZE,
                                           roster_extra, trans);
        if (!name)
        {
            Py_DECREF(roster_extra);
            Py_DECREF(roster);
            return NULL;
        }
        PyList_SET_ITEM(roster, (Py_ssize_t)i, name);
    }

    Py_DECREF(roster_extra);
    return roster;
}

/* ===================================================================
 * 重建描述区域
 *
 * 将 \n 分隔的文本用 00 00 连接，末尾追加 00 00，
 * CD 填充到 48 的整数倍。
 * =================================================================== */

static int _build_description(
    unsigned char *buf, size_t buf_size,
    PyObject *desc_text, PyObject *extra, PyObject *trans,
    size_t *out_total)
{
    *out_total = 0;

    if (!desc_text || desc_text == Py_None)
    {
        /* 无描述：只写 00 00 */
        if (buf_size >= 2)
        {
            buf[0] = 0x00;
            buf[1] = 0x00;
            *out_total = 2;
        }
        return 0;
    }

    /* 转为 UTF-8 并拆行 */
    PyObject *utf8 = PyUnicode_AsUTF8String(desc_text);
    if (!utf8)
        return -1;

    const char *desc_str = PyBytes_AsString(utf8);
    Py_ssize_t desc_len = PyBytes_Size(utf8);

    enum { MAX_LINES = 128 };
    const char *line_starts[MAX_LINES];
    Py_ssize_t line_lengths[MAX_LINES];
    Py_ssize_t num_lines = 0;
    const char *p = desc_str;
    const char *end = desc_str + desc_len;

    while (p < end && num_lines < MAX_LINES)
    {
        const char *nl = (const char *)memchr(p, '\n', (size_t)(end - p));
        line_starts[num_lines] = p;
        line_lengths[num_lines] = nl ? (nl - p) : (end - p);
        p = nl ? (nl + 1) : end;
        num_lines++;
    }

    /* 找最后一条非空行的索引 */
    Py_ssize_t last_line_idx = -1;
    for (Py_ssize_t i = num_lines - 1; i >= 0; i--)
    {
        if (line_lengths[i] > 0) { last_line_idx = i; break; }
    }

    /* 逐行编码并写入，每行独立 48B cell 掩码 */
    /* 非末行: text + 00 00 + CD     末行: text + term + CD  */
    /* 末行终止符根据 dsize % 48 选择: 0 → 无, 47 → 单 00, 否则 → 00 00 */
    size_t off = 0;
    for (Py_ssize_t i = 0; i < num_lines; i++)
    {
        if (line_lengths[i] == 0)
            continue;

        int is_last = (i == last_line_idx);

        PyObject *line_str = PyUnicode_DecodeUTF8(
            line_starts[i], line_lengths[i], NULL);
        if (!line_str)
            continue;

        PyObject *encoded = codec_encode(line_str, extra, trans);
        Py_DECREF(line_str);
        if (!encoded)
            continue;

        const char *data = PyBytes_AsString(encoded);
        Py_ssize_t dsize = PyBytes_Size(encoded);
        if (!data || dsize < 0)
        {
            Py_DECREF(encoded);
            continue;
        }

        /* 确定终止符长度 */
        int term_len;
        if (!is_last)
        {
            term_len = 2; /* 非末行固定 00 00 */
        }
        else if (dsize % 48 == 0 && dsize > 0)
        {
            term_len = 0; /* 末行恰好满 cell，可省略终止符 */
        }
        else if (dsize % 48 == 47)
        {
            term_len = 1; /* 末行 00 00 放不下，退化为单 00 */
        }
        else
        {
            term_len = 2; /* 末行正常 00 00 */
        }

        size_t cell_total = (size_t)dsize + (size_t)term_len;
        size_t rem = cell_total % DR_DESC_CELL_SIZE;
        if (rem > 0)
            cell_total += DR_DESC_CELL_SIZE - rem;

        if (off + cell_total > buf_size)
        {
            Py_DECREF(encoded);
            return -1;
        }

        size_t cell_start = off;
        memcpy(buf + off, data, (size_t)dsize);
        off += (size_t)dsize;
        if (term_len >= 1)
            buf[off++] = 0x00;
        if (term_len >= 2)
            buf[off++] = 0x00;

        /* CD 填到 cell 尾部 */
        size_t cell_end = cell_start + cell_total;
        while (off < cell_end)
            buf[off++] = 0xCD;

        Py_DECREF(encoded);
    }

    Py_DECREF(utf8);

    /* 无文本时写一个空 cell */
    if (off == 0)
    {
        if (buf_size < DR_DESC_CELL_SIZE)
            return -1;
        memset(buf, 0xCD, DR_DESC_CELL_SIZE);
        buf[0] = 0x00;
        buf[1] = 0x00;
        *out_total = DR_DESC_CELL_SIZE;
        return 0;
    }

    *out_total = off;
    return 0;
}

/* ===================================================================
 * 重建块 0（机体名册）
 * =================================================================== */

static unsigned char *_build_roster(
    PyObject *roster_list, size_t record_count,
    PyObject *extra, PyObject *trans,
    size_t *out_comp_size)
{
    PyObject *roster_extra = _make_roster_extra(extra);
    if (!roster_extra)
        return NULL;

    size_t decomp_size = record_count * DR_ROSTER_SLOT_SIZE;
    unsigned char *decomp = (unsigned char *)malloc(decomp_size);
    if (!decomp)
    {
        Py_DECREF(roster_extra);
        return NULL;
    }
    memset(decomp, 0xCD, decomp_size);

    for (size_t i = 0; i < record_count; i++)
    {
        PyObject *name = PyList_GetItem(roster_list, (Py_ssize_t)i);
        if (!name)
            continue;

        size_t slot_off = i * DR_ROSTER_SLOT_SIZE;

        PyObject *encoded = codec_encode(name, roster_extra, trans);
        if (!encoded)
            continue;

        Py_ssize_t enc_len = PyBytes_Size(encoded);
        if (enc_len < 0)
        {
            Py_DECREF(encoded);
            continue;
        }

        size_t max_text = DR_ROSTER_SLOT_SIZE - 1;
        if ((size_t)enc_len > max_text)
            enc_len = (Py_ssize_t)max_text;

        const char *enc_data = PyBytes_AsString(encoded);
        if (enc_data)
        {
            memcpy(decomp + slot_off, enc_data, (size_t)enc_len);
            decomp[slot_off + enc_len] = 0x00;

            /* 统计首个双字节字符之后的半角 ASCII 数（排除机型前缀和半角假名）
             * 规则同 DC：只计 ASCII 非字母字符（排除 A-Z a-z）
             * 末尾追加 N 个 00，N = 该数目 */
            size_t trail = 0;
            int seen_double = 0;
            {
                Py_ssize_t k = 0;
                while (k < enc_len) {
                    unsigned char b = (unsigned char)enc_data[k];
                    if (b < 0x80) {
                        if (seen_double && b >= 0x21 && b <= 0x7E) {
                            int is_letter = (b >= 0x41 && b <= 0x5A)
                                         || (b >= 0x61 && b <= 0x7A);
                            if (!is_letter) trail++;
                        }
                        k++;
                    } else if (b >= 0xA1 && b <= 0xDF) {
                        k++; /* 半角假名不计入 */
                    } else {
                        seen_double = 1;
                        k += 2; /* 双字节字符 */
                    }
                }
            }

            size_t end = slot_off + DR_ROSTER_SLOT_SIZE;
            for (size_t t = 0; t < trail && t < DR_ROSTER_SLOT_SIZE; t++)
                decomp[end - 1 - t] = 0x00;
        }

        Py_DECREF(encoded);
    }

    Py_DECREF(roster_extra);
    unsigned char *comp = _compress_block(decomp, decomp_size, out_comp_size);
    free(decomp);
    return comp;
}

/* ===================================================================
 * 重建机体详情块
 * =================================================================== */

static unsigned char *_build_robot(
    PyObject *robot_dict,
    PyObject *extra, PyObject *trans,
    size_t *out_comp_size)
{
    /* 先构建描述文本，确定解压缓冲区大小 */
    /* 临时缓冲区用于计算描述大小 */
    enum { TEMP_BUF_SIZE = 65536 };
    unsigned char *temp_buf = (unsigned char *)malloc(TEMP_BUF_SIZE);
    if (!temp_buf)
        return NULL;

    size_t desc_total = 0;
    PyObject *desc = PyDict_GetItemString(robot_dict, "desc");
    int build_ret = _build_description(temp_buf, TEMP_BUF_SIZE,
                                        desc, extra, trans, &desc_total);
    if (build_ret != 0)
    {
        free(temp_buf);
        return NULL;
    }

    /* 解压缓冲区大小 = 固定头部 + 描述数据 */
    size_t decomp_size = DR_OFF_DESC_START + desc_total;
    if (decomp_size < DR_OFF_DESC_START)
        decomp_size = DR_OFF_DESC_START;

    unsigned char *decomp = (unsigned char *)malloc(decomp_size);
    if (!decomp)
    {
        free(temp_buf);
        return NULL;
    }
    memset(decomp, 0xCD, decomp_size);

    /* 写入描述文本 */
    if (desc_total > 0 && DR_OFF_DESC_START + desc_total <= decomp_size)
        memcpy(decomp + DR_OFF_DESC_START, temp_buf, desc_total);
    free(temp_buf);

    /* 覆写字段 */

    /* 机体名 @ 0x00 */
    {
        PyObject *v = PyDict_GetItemString(robot_dict, "name");
        if (v && v != Py_None)
            _write_text_field(decomp, decomp_size, DR_OFF_NAME,
                              DR_SLOT_NAME, v, extra, trans);
    }

    /* 全高 @ 0x30 */
    {
        PyObject *v = PyDict_GetItemString(robot_dict, "height");
        if (v && v != Py_None)
            _write_text_field(decomp, decomp_size, DR_OFF_HEIGHT,
                              DR_SLOT_HEIGHT, v, extra, trans);
    }

    /* 重量 @ 0x50 */
    {
        PyObject *v = PyDict_GetItemString(robot_dict, "weight");
        if (v && v != Py_None)
            _write_text_field(decomp, decomp_size, DR_OFF_WEIGHT,
                              DR_SLOT_WEIGHT, v, extra, trans);
    }

    /* 出身 @ 0x70 */
    {
        PyObject *v = PyDict_GetItemString(robot_dict, "appr");
        if (v && v != Py_None)
            _write_text_field(decomp, decomp_size, DR_OFF_APPR,
                              DR_SLOT_APPR, v, extra, trans);
    }

    /* flags @ 0xB0 */
    {
        PyObject *v = PyDict_GetItemString(robot_dict, "flags");
        if (v && v != Py_None)
        {
            if (DR_OFF_FLAGS + DR_SIZE_FLAGS <= decomp_size)
            {
                unsigned long flags = PyLong_AsUnsignedLong(v);
                if (flags == (unsigned long)-1 && PyErr_Occurred())
                    PyErr_Clear();
                else
                    _write_le32(decomp + DR_OFF_FLAGS, (uint32_t)flags);
            }
        }
    }

    /* LZSS 压缩 */
    unsigned char *comp = _compress_block(decomp, decomp_size, out_comp_size);
    free(decomp);
    return comp;
}

/* ===================================================================
 * Python API: parse(data, extra=None, trans=None) -> dict
 * =================================================================== */

static PyObject *
dr_bin_parse(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"data", "extra", "trans", NULL};
    Py_buffer view;
    PyObject *extra = Py_None;
    PyObject *trans = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y*|OO", (char **)kwlist,
                                     &view, &extra, &trans))
        return NULL;

    const unsigned char *data = (const unsigned char *)view.buf;
    size_t data_size = view.len;

    if (data_size < DR_PTR_TABLE_SIZE)
    {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_ValueError, "DR.BIN: data too small");
        return NULL;
    }

    /* 读取指针 */
    uint32_t ptrs[DR_PTR_COUNT];
    for (int i = 0; i < DR_PTR_COUNT; i++)
        ptrs[i] = _read_le32(data + (size_t)i * 4);

    if (ptrs[0] != DR_PTR_TABLE_SIZE ||
        ptrs[DR_PTR_COUNT - 1] != (uint32_t)data_size)
    {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_ValueError,
                        "DR.BIN: invalid pointer table");
        return NULL;
    }

    int block_count = DR_PTR_COUNT - 1; /* 449 个块 */

    /* ===== 块 0: 名册 ===== */
    size_t blk0_comp_start = ptrs[0];
    size_t blk0_comp_end = ptrs[1];
    size_t blk0_comp_size = blk0_comp_end - blk0_comp_start;

    size_t decomp_size = 0;
    unsigned char *decomp = _decompress_block(
        data + blk0_comp_start, blk0_comp_size, &decomp_size);
    if (!decomp)
    {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_RuntimeError,
                        "DR.BIN: failed to decompress block 0");
        return NULL;
    }

    PyObject *roster = _parse_roster(decomp, decomp_size, extra, trans);
    free(decomp);
    if (!roster)
    {
        PyBuffer_Release(&view);
        return NULL;
    }

    Py_ssize_t robot_count = PyList_Size(roster);

    /* ===== 块 1~448: 机体详情 ===== */
    PyObject *dr_list = PyList_New(robot_count);
    if (!dr_list)
    {
        Py_DECREF(roster);
        PyBuffer_Release(&view);
        return NULL;
    }

    for (int i = 0; i < robot_count; i++)
    {
        size_t comp_start = ptrs[i + 1];
        size_t comp_end = ptrs[i + 2];
        size_t comp_size = comp_end - comp_start;

        decomp_size = 0;
        decomp = _decompress_block(data + comp_start, comp_size, &decomp_size);
        if (!decomp)
        {
            Py_DECREF(roster);
            Py_DECREF(dr_list);
            PyBuffer_Release(&view);
            PyErr_Format(PyExc_RuntimeError,
                         "DR.BIN: failed to decompress block %d", i + 1);
            return NULL;
        }

        PyObject *robot_dict = _parse_robot(decomp, decomp_size,
                                             extra, trans);
        free(decomp);

        if (!robot_dict)
        {
            Py_DECREF(roster);
            Py_DECREF(dr_list);
            PyBuffer_Release(&view);
            return NULL;
        }

        PyList_SET_ITEM(dr_list, (Py_ssize_t)i, robot_dict);
    }

    PyBuffer_Release(&view);

    PyObject *result = PyDict_New();
    if (!result)
    {
        Py_DECREF(roster);
        Py_DECREF(dr_list);
        return NULL;
    }

    PyDict_SetItemString(result, "name", PyUnicode_FromString("dr"));
    PyDict_SetItemString(result, "count",
                         PyLong_FromSsize_t(robot_count));
    PyDict_SetItemString(result, "roster", roster);
    PyDict_SetItemString(result, "dr", dr_list);

    Py_DECREF(roster);
    Py_DECREF(dr_list);
    return result;
}

/* ===================================================================
 * Python API: build(data, extra=None, trans=None) -> bytearray
 * =================================================================== */

static PyObject *
dr_bin_build(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"data", "extra", "trans", NULL};
    PyObject *data_dict = NULL;
    PyObject *extra = Py_None;
    PyObject *trans = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|OO", (char **)kwlist,
                                     &data_dict, &extra, &trans))
        return NULL;

    if (!PyDict_Check(data_dict))
    {
        PyErr_SetString(PyExc_TypeError,
                        "DR.BIN build: expected dict argument");
        return NULL;
    }

    PyObject *roster = PyDict_GetItemString(data_dict, "roster");
    if (!roster || !PyList_Check(roster))
    {
        PyErr_SetString(PyExc_ValueError,
                        "DR.BIN build: 'roster' must be a list");
        return NULL;
    }

    PyObject *dr_list = PyDict_GetItemString(data_dict, "dr");
    if (!dr_list || !PyList_Check(dr_list))
    {
        PyErr_SetString(PyExc_ValueError,
                        "DR.BIN build: 'dr' must be a list");
        return NULL;
    }

    Py_ssize_t robot_count = PyList_Size(dr_list);
    Py_ssize_t roster_count = PyList_Size(roster);

    if (roster_count < robot_count)
    {
        PyErr_SetString(PyExc_ValueError,
                        "DR.BIN build: roster count < robot count");
        return NULL;
    }

    /* 构建各块压缩数据 */
    int block_count = (int)robot_count + 1;
    unsigned char **comp_blocks = (unsigned char **)malloc(
        (size_t)block_count * sizeof(unsigned char *));
    size_t *comp_sizes = (size_t *)malloc(
        (size_t)block_count * sizeof(size_t));

    if (!comp_blocks || !comp_sizes)
    {
        free(comp_blocks);
        free(comp_sizes);
        return NULL;
    }

    /* 块 0: 名册 */
    comp_blocks[0] = _build_roster(roster, (size_t)roster_count,
                                    extra, trans, &comp_sizes[0]);
    if (!comp_blocks[0])
    {
        free(comp_blocks);
        free(comp_sizes);
        return NULL;
    }

    /* 块 1~N: 机体详情 */
    for (Py_ssize_t i = 0; i < robot_count; i++)
    {
        PyObject *robot_dict = PyList_GetItem(dr_list, i);
        if (!robot_dict || !PyDict_Check(robot_dict))
        {
            PyErr_Format(PyExc_TypeError,
                         "DR.BIN build: dr[%d] must be a dict",
                         (int)i);
            for (Py_ssize_t j = 0; j <= i; j++)
                free(comp_blocks[j]);
            free(comp_blocks);
            free(comp_sizes);
            return NULL;
        }

        comp_blocks[i + 1] = _build_robot(robot_dict, extra, trans,
                                           &comp_sizes[i + 1]);
        if (!comp_blocks[i + 1])
        {
            for (Py_ssize_t j = 0; j <= i; j++)
                free(comp_blocks[j]);
            free(comp_blocks);
            free(comp_sizes);
            return NULL;
        }
    }

    /* 计算总大小并拼接 */
    size_t total_size = DR_PTR_TABLE_SIZE;
    for (int i = 0; i < block_count; i++)
        total_size += comp_sizes[i];

    unsigned char *output = (unsigned char *)malloc(total_size);
    if (!output)
    {
        for (int i = 0; i < block_count; i++)
            free(comp_blocks[i]);
        free(comp_blocks);
        free(comp_sizes);
        return NULL;
    }

    /* 指针表 */
    size_t cur_offset = 0;
    for (int i = 0; i < block_count + 1; i++)
    {
        uint32_t ptr_value = DR_PTR_TABLE_SIZE + (uint32_t)cur_offset;
        _write_le32(output + (size_t)i * 4, ptr_value);
        if (i < block_count)
            cur_offset += comp_sizes[i];
    }

    /* 数据区 */
    unsigned char *data_ptr = output + DR_PTR_TABLE_SIZE;
    for (int i = 0; i < block_count; i++)
    {
        memcpy(data_ptr, comp_blocks[i], comp_sizes[i]);
        data_ptr += comp_sizes[i];
        free(comp_blocks[i]);
    }

    free(comp_blocks);
    free(comp_sizes);

    PyObject *result = PyByteArray_FromStringAndSize(
        (const char *)output, (Py_ssize_t)total_size);
    free(output);
    return result;
}

/* ===================================================================
 * 模块定义
 * =================================================================== */

static PyMethodDef dr_bin_methods[] = {
    {"parse", (PyCFunction)dr_bin_parse, METH_VARARGS | METH_KEYWORDS,
     "parse(data, extra=None, trans=None) -> dict\n\n"
     "Decompress and parse DR.BIN into a Python dict.\n"
     "Returns {name, count, roster, dr}."},
    {"build", (PyCFunction)dr_bin_build, METH_VARARGS | METH_KEYWORDS,
     "build(data, extra=None, trans=None) -> bytearray\n\n"
     "Build DR.BIN binary from a Python dict."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef dr_bin_module = {
    PyModuleDef_HEAD_INIT,
    "_dr_bin",
    "DR.BIN parser/builder for Super Robot Wars Alpha ROM Editor",
    -1,
    dr_bin_methods
};

PyMODINIT_FUNC
PyInit__dr_bin(void)
{
    return PyModule_Create(&dr_bin_module);
}
