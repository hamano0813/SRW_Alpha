/*
 * dc_bin.c -- DC.BIN parser/builder C extension
 *
 * DC.BIN 是角色图鉴数据文件，包含 350 个 LZSS 压缩块：
 *   块 0 — 角色名册（349 × 0x30 字节记录）
 *   块 1~349 — 各角色详情（固定偏移字段 + 0x30 对齐描述行）
 *
 * 文件格式：
 *   0x0000~0x057B  指针表（351 × uint32 LE）
 *   0x057C~EOF      数据区（LZSS 压缩块）
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
#define DC_OFF_FULL_NAME    0x00   /* 完整名 */
#define DC_SLOT_FULL_NAME   0x30
#define DC_OFF_SHORT_NAME   0x30   /* 缩写名 */
#define DC_SLOT_SHORT_NAME  0x14
#define DC_OFF_SERIES       0x44   /* 出处作品 */
#define DC_SLOT_SERIES      0x40
#define DC_OFF_VOICE_ACTOR  0x84   /* 声优 — 文本区 20 字节，后续 flag@0x98 */
#define DC_SLOT_VOICE_ACTOR 0x14
#define DC_ZERO_PAD_START   0x99   /* flag 后的 3 字节固定零区 */
#define DC_ZERO_PAD_SIZE    3
#define DC_OFF_FLAG         0x98   /* 标识字节（F04 槽内固定偏移） */
#define DC_OFF_DESC_START   0x9C   /* 描述文本起始偏移 */
#define DC_DESC_CELL_SIZE   0x30   /* 每行描述文本的 0x30 槽 */

/* 块 0 名册记录大小 */
#define DC_ROSTER_SLOT_SIZE 0x30

/* 指针表大小 */
#define DC_PTR_TABLE_SIZE   0x57C
#define DC_PTR_COUNT        351

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
 * 解压单个 LZSS 块
 *
 * 返回解压后的数据（caller 负责 free），失败返回 NULL。
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

/* ===================================================================
 * 压缩单个 LZSS 块
 *
 * 返回压缩后的数据（caller 负责 free），失败返回 NULL。
 * =================================================================== */

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
 * 返回写入的字节数（含 00 终结符），出错返回 -1。
 * =================================================================== */

static Py_ssize_t _write_text_field(
    unsigned char *buf, size_t buf_size, size_t offset, size_t slot_size,
    PyObject *text, PyObject *extra, PyObject *trans)
{
    if (offset + slot_size > buf_size)
        return -1;

    /* 编码文本 */
    PyObject *encoded = codec_encode(text, extra, trans);
    if (!encoded)
        return -1;

    Py_ssize_t text_len = PyBytes_Size(encoded);
    if (text_len < 0)
    {
        Py_DECREF(encoded);
        return -1;
    }

    /* 文本不能超过槽大小 - 1（留 1 字节给 00） */
    if ((size_t)text_len >= slot_size)
        text_len = (Py_ssize_t)(slot_size - 1);

    char *enc_buf = PyBytes_AsString(encoded);
    if (!enc_buf)
    {
        Py_DECREF(encoded);
        return -1;
    }

    memcpy(buf + offset, enc_buf, (size_t)text_len);
    buf[offset + text_len] = 0x00; /* 00 终结符 */

    Py_DECREF(encoded);
    return text_len + 1; /* 文本字节数 + 00 */
}

/* ===================================================================
 * 统计 Shift-JIS 编码文本中的半角 ASCII 字符数
 *
 * 双字节字符正确跳过，英文字母（A-Z, a-z）视为全角不计入。
 * 用于名册记录的末尾 00 规则：末尾 00 数 == 半角 ASCII 数。
 * =================================================================== */

static size_t _count_halfwidth_ascii(const char *sjis_bytes, size_t len)
{
    size_t count = 0;
    size_t i = 0;

    while (i < len) {
        unsigned char b = (unsigned char)sjis_bytes[i];
        if (b == 0x00)
            break;
        if ((b >= 0x81 && b <= 0x9F) || (b >= 0xE0 && b <= 0xFC)) {
            /* 双字节 Shift-JIS 字符 */
            i += 2;
        } else if (b <= 0x7F) {
            /* 单字节 ASCII，排除英文字母（视为全角） */
            if (b >= 0x21 && b <= 0x7E) {
                if (!((b >= 0x41 && b <= 0x5A) || (b >= 0x61 && b <= 0x7A)))
                    count++;
            }
            i += 1;
        } else {
            /* 半角片假名区 0xA0-0xDF */
            i += 1;
        }
    }
    return count;
}

/* ===================================================================
 * 名册专用 extra 映射
 *
 * 在现有 extra 基础上叠加 {'-': 'ー'}，供 _parse_roster 解码
 * 和 _build_roster 编码（反向时 ー→-）使用。
 * 返回新 dict，caller 负责 Py_DECREF。extra 为 Py_None 或 NULL 时
 * 返回仅含该映射的新 dict。
 * =================================================================== */

static PyObject *_make_roster_extra(PyObject *extra)
{
    PyObject *roster_extra;
    if (extra && extra != Py_None)
        roster_extra = PyDict_Copy(extra);
    else
        roster_extra = PyDict_New();

    if (!roster_extra)
        return NULL;

    PyObject *k = PyUnicode_FromString("-");
    PyObject *v = PyUnicode_FromString("ー");
    if (k && v)
        PyDict_SetItem(roster_extra, k, v);
    Py_XDECREF(k);
    Py_XDECREF(v);

    return roster_extra;
}

/* ===================================================================
 * 解析块 0（角色名册）→ Python list of str
 * =================================================================== */

static PyObject *_parse_roster(
    const unsigned char *data, size_t size,
    PyObject *extra, PyObject *trans)
{
    if (size < DC_ROSTER_SLOT_SIZE)
        return NULL;

    size_t count = size / DC_ROSTER_SLOT_SIZE;

    PyObject *roster = PyList_New((Py_ssize_t)count);
    if (!roster)
        return NULL;

    /* 名册专用映射：'-' → 'ー'（半角连字符→全角长音） */
    PyObject *roster_extra = _make_roster_extra(extra);
    if (!roster_extra)
    {
        Py_DECREF(roster);
        return NULL;
    }

    for (size_t i = 0; i < count; i++)
    {
        size_t offset = i * DC_ROSTER_SLOT_SIZE;
        PyObject *name = _read_text_field(data, size, offset,
                                          DC_ROSTER_SLOT_SIZE, roster_extra, trans);
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
 * 解析描述文本行
 *
 * 从 offset 开始扫描，00 终结一段，连续 00 为强制换行。
 * 所有行用 \n 拼接为一个字符串。
 * =================================================================== */

static PyObject *_parse_description(
    const unsigned char *buf, size_t buf_size, size_t start_offset,
    PyObject *extra, PyObject *trans)
{
    /* 先收集所有行 */
    Py_ssize_t max_lines = 256;
    char **lines = (char **)malloc((size_t)max_lines * sizeof(char *));
    Py_ssize_t *line_lens = (Py_ssize_t *)malloc((size_t)max_lines * sizeof(Py_ssize_t));
    if (!lines || !line_lens)
    {
        free(lines);
        free(line_lens);
        return NULL;
    }

    Py_ssize_t line_count = 0;
    size_t pos = start_offset;

    while (pos < buf_size)
    {
        /* 找下一个 00 */
        size_t null_pos = pos;
        while (null_pos < buf_size && buf[null_pos] != 0x00)
            null_pos++;

        size_t seg_len = null_pos - pos;

        if (seg_len > 0)
        {
            /* 跳过 cd 前导 */
            size_t cd_skip = 0;
            while (cd_skip < seg_len && buf[pos + cd_skip] == 0xCD)
                cd_skip++;

            if (cd_skip >= seg_len)
            {
                /* 整段都是 cd，跳过 */
                pos = null_pos + 1;
                continue;
            }

            /* 解码这一行（跳过 cd 前导） */
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

            /* 转换为 UTF-8 C string 暂存 */
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
            memcpy(lines[line_count], PyBytes_AsString(utf8), (size_t)utf8_len);
            lines[line_count][utf8_len] = '\0';
            line_lens[line_count] = utf8_len;
            Py_DECREF(utf8);
            line_count++;

            if (line_count >= max_lines)
                break;
        }

        /* 跳过 00 */
        pos = null_pos + 1;

        /* 连续 00 表示行分隔符，跳过后续 00 */
        if (pos < buf_size && buf[pos] == 0x00)
        {
            if (seg_len > 0)
            {
                /* 在上一行末尾追加 \n */
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
            pos++; /* 跳过第二个 00 */
        }
    }

    /* 拼接所有行 */
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
    return result;
}

/* ===================================================================
 * 解析单个角色详情块
 *
 * 保存原始解压数据 _raw 用于 build 阶段的字节级还原。
 * =================================================================== */

static PyObject *_parse_character(
    const unsigned char *decomp, size_t decomp_size,
    PyObject *extra, PyObject *trans)
{
    PyObject *char_dict = PyDict_New();
    if (!char_dict)
        return NULL;

    /* F00: 完整名 @ 0x00 */
    {
        PyObject *v = _read_text_field(decomp, decomp_size, DC_OFF_FULL_NAME,
                                       DC_SLOT_FULL_NAME, extra, trans);
        if (!v) { Py_DECREF(char_dict); return NULL; }
        PyDict_SetItemString(char_dict, "fname", v);
        Py_DECREF(v);
    }

    /* F01: 缩写名 @ 0x30 */
    {
        PyObject *v = _read_text_field(decomp, decomp_size, DC_OFF_SHORT_NAME,
                                       DC_SLOT_SHORT_NAME, extra, trans);
        if (!v) { Py_DECREF(char_dict); return NULL; }
        PyDict_SetItemString(char_dict, "pname", v);
        Py_DECREF(v);
    }

    /* F02: 出处作品 @ 0x44 */
    {
        PyObject *v = _read_text_field(decomp, decomp_size, DC_OFF_SERIES,
                                       DC_SLOT_SERIES, extra, trans);
        if (!v) { Py_DECREF(char_dict); return NULL; }
        PyDict_SetItemString(char_dict, "appr", v);
        Py_DECREF(v);
    }

    /* F03: 声优 @ 0x84 */
    {
        PyObject *v = _read_text_field(decomp, decomp_size, DC_OFF_VOICE_ACTOR,
                                       DC_SLOT_VOICE_ACTOR, extra, trans);
        if (!v) { Py_DECREF(char_dict); return NULL; }
        PyDict_SetItemString(char_dict, "voice", v);
        Py_DECREF(v);
    }

    /* F04: 标识字节 @ 0x98 */
    if (DC_OFF_FLAG < decomp_size)
    {
        int flag = (int)decomp[DC_OFF_FLAG];
        PyObject *v = PyLong_FromLong(flag);
        if (!v) { Py_DECREF(char_dict); return NULL; }
        PyDict_SetItemString(char_dict, "flags", v);
        Py_DECREF(v);
    }

    /* 描述文本（从 0x9C 开始，含 cd 前导） */
    if (DC_OFF_DESC_START < decomp_size)
    {
        PyObject *desc = _parse_description(decomp, decomp_size,
                                            DC_OFF_DESC_START, extra, trans);
        if (!desc) { Py_DECREF(char_dict); return NULL; }
        PyDict_SetItemString(char_dict, "desc", desc);
        Py_DECREF(desc);
    }
    else
    {
        PyDict_SetItemString(char_dict, "desc",
                             PyUnicode_FromString(""));
    }

    return char_dict;
}

/* ===================================================================
 * 重建描述区域
 *
 * 将 \n 分隔的文本拆行，逐行写入 0x30 槽位。
 * 每行：文本左对齐 + 00 + cd 补齐。非最后一行追加分隔 00。
 * =================================================================== */

static int _build_description(
    unsigned char *buf, size_t buf_size,
    PyObject *desc_text, PyObject *extra, PyObject *trans,
    size_t *out_num_cells)
{
    *out_num_cells = 0;
    if (!desc_text || desc_text == Py_None)
        return 0;

    /* 转为 UTF-8 */
    PyObject *utf8 = PyUnicode_AsUTF8String(desc_text);
    if (!utf8)
        return -1;

    const char *desc_str = PyBytes_AsString(utf8);
    Py_ssize_t desc_len = PyBytes_Size(utf8);
    if (!desc_str || desc_len < 0)
    {
        Py_DECREF(utf8);
        return -1;
    }

    /* 拆行 */
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
        if (nl)
        {
            line_lengths[num_lines] = nl - p;
            p = nl + 1;
        }
        else
        {
            line_lengths[num_lines] = end - p;
            p = end;
        }
        num_lines++;
    }

    /* 逐行写入 */
    size_t cell = 0;
    size_t cell_offset = DC_OFF_DESC_START;

    for (Py_ssize_t i = 0; i < num_lines; i++)
    {
        /* 跳过空行 */
        if (line_lengths[i] == 0)
            continue;

        if (cell_offset + DC_DESC_CELL_SIZE > buf_size)
            break;

        /* 编码本行 */
        PyObject *line_str = PyUnicode_DecodeUTF8(
            line_starts[i], line_lengths[i], NULL);
        if (!line_str)
            continue;

        PyObject *encoded = codec_encode(line_str, extra, trans);
        Py_DECREF(line_str);
        if (!encoded)
            continue;

        Py_ssize_t enc_len = PyBytes_Size(encoded);
        if (enc_len < 0)
        {
            Py_DECREF(encoded);
            continue;
        }
        /* 至少留 2 字节给 00 + 分隔 00 */
        size_t max_text = DC_DESC_CELL_SIZE - 2;
        if ((size_t)enc_len > max_text)
            enc_len = (Py_ssize_t)max_text;

        const char *enc_data = PyBytes_AsString(encoded);
        if (enc_data)
        {
            memcpy(buf + cell_offset, enc_data, (size_t)enc_len);
            buf[cell_offset + enc_len] = 0x00;
            /* 写分隔 00：非最后一行必写；最后一行仅当末尾带 \n 时写 */
            if (i + 1 < num_lines ||
                (desc_len > 0 && desc_str[desc_len - 1] == '\n'))
                buf[cell_offset + enc_len + 1] = 0x00;
        }
        Py_DECREF(encoded);

        cell_offset += DC_DESC_CELL_SIZE;
        cell++;
    }

    *out_num_cells = (size_t)num_lines;
    Py_DECREF(utf8);
    return 0;
}

/* ===================================================================
 * 重建角色详情块（从零构建解压缓冲区 → LZSS 压缩）
 * =================================================================== */

static unsigned char *_build_character(
    PyObject *char_dict,
    PyObject *extra, PyObject *trans,
    size_t *out_comp_size)
{
    /* 计算描述行数 → 解压缓冲区大小 */
    PyObject *desc = PyDict_GetItemString(char_dict, "desc");
    size_t num_desc_lines = 0;
    if (desc && desc != Py_None && PyUnicode_Check(desc))
    {
        Py_ssize_t desc_len = 0;
        const char *desc_u8 = PyUnicode_AsUTF8AndSize(desc, &desc_len);
        if (desc_u8 && desc_len > 0)
        {
            /* 去掉末尾 \n（parse 阶段对最后一个 00 00 也追加了 \n） */
            Py_ssize_t effective_len = desc_len;
            if (desc_u8[desc_len - 1] == '\n')
                effective_len--;

            for (Py_ssize_t i = 0; i < effective_len; i++)
                if (desc_u8[i] == '\n')
                    num_desc_lines++;
            num_desc_lines++; /* 最后一行 */
        }
    }

    size_t decomp_size = DC_OFF_DESC_START + num_desc_lines * DC_DESC_CELL_SIZE;
    if (decomp_size < DC_OFF_DESC_START)
        decomp_size = DC_OFF_DESC_START;

    /* mask 全 CD 填充，覆写文本 */
    unsigned char *decomp = (unsigned char *)malloc(decomp_size);
    if (!decomp)
        return NULL;
    memset(decomp, 0xCD, decomp_size);

    /* 覆写 F00: 完整名 @ 0x00 */
    {
        PyObject *v = PyDict_GetItemString(char_dict, "fname");
        if (v && v != Py_None)
            _write_text_field(decomp, decomp_size, DC_OFF_FULL_NAME,
                              DC_SLOT_FULL_NAME, v, extra, trans);
    }

    /* 覆写 F01: 缩写名 @ 0x30 */
    {
        PyObject *v = PyDict_GetItemString(char_dict, "pname");
        if (v && v != Py_None)
            _write_text_field(decomp, decomp_size, DC_OFF_SHORT_NAME,
                              DC_SLOT_SHORT_NAME, v, extra, trans);
    }

    /* 覆写 F02: 出处作品 @ 0x44 */
    {
        PyObject *v = PyDict_GetItemString(char_dict, "appr");
        if (v && v != Py_None)
            _write_text_field(decomp, decomp_size, DC_OFF_SERIES,
                              DC_SLOT_SERIES, v, extra, trans);
    }

    /* 覆写 F03: 声优 @ 0x84 */
    {
        PyObject *v = PyDict_GetItemString(char_dict, "voice");
        if (v && v != Py_None)
            _write_text_field(decomp, decomp_size, DC_OFF_VOICE_ACTOR,
                              DC_SLOT_VOICE_ACTOR, v, extra, trans);
    }

    /* 覆写 F04: 标识字节 @ 0x98 */
    {
        PyObject *v = PyDict_GetItemString(char_dict, "flags");
        if (v && v != Py_None)
        {
            long flag = PyLong_AsLong(v);
            if (flag >= 0 && flag <= 255 && DC_OFF_FLAG < decomp_size)
                decomp[DC_OFF_FLAG] = (unsigned char)flag;
        }
    }

    /* 0x99-0x9B: flag 后的 3 字节固定零区 */
    if (DC_ZERO_PAD_START + DC_ZERO_PAD_SIZE <= decomp_size)
        memset(decomp + DC_ZERO_PAD_START, 0x00, DC_ZERO_PAD_SIZE);

    /* 构建描述文本 */
    {
        size_t cells = 0;
        _build_description(decomp, decomp_size, desc, extra, trans, &cells);
    }

    /* LZSS 压缩 */
    unsigned char *comp = _compress_block(decomp, decomp_size, out_comp_size);
    free(decomp);
    return comp;
}

/* ===================================================================
 * 重建块 0（角色名册）
 * =================================================================== */

static unsigned char *_build_roster(
    PyObject *roster_list, size_t record_count,
    PyObject *extra, PyObject *trans,
    size_t *out_comp_size)
{
    size_t decomp_size = record_count * DC_ROSTER_SLOT_SIZE;
    unsigned char *decomp = (unsigned char *)malloc(decomp_size);
    if (!decomp)
        return NULL;
    memset(decomp, 0xCD, decomp_size);

    /* 名册专用映射：编码反向时 ー→-（与 _parse_roster 对称） */
    PyObject *roster_extra = _make_roster_extra(extra);
    if (!roster_extra)
    {
        free(decomp);
        return NULL;
    }

    for (size_t i = 0; i < record_count; i++)
    {
        PyObject *name = PyList_GetItem(roster_list, (Py_ssize_t)i);
        if (!name)
            continue;

        size_t slot_off = i * DC_ROSTER_SLOT_SIZE;

        /* 编码文本 */
        PyObject *encoded = codec_encode(name, roster_extra, trans);
        if (!encoded)
            continue;

        Py_ssize_t enc_len = PyBytes_Size(encoded);
        if (enc_len < 0)
        {
            Py_DECREF(encoded);
            continue;
        }

        /* 限制在槽大小 - 1 以内（留 1 字节给 00） */
        size_t max_text = DC_ROSTER_SLOT_SIZE - 1;
        if ((size_t)enc_len > max_text)
            enc_len = (Py_ssize_t)max_text;

        const char *enc_data = PyBytes_AsString(encoded);
        if (enc_data)
        {
            /* 覆写文本 + 00 */
            memcpy(decomp + slot_off, enc_data, (size_t)enc_len);
            decomp[slot_off + enc_len] = 0x00;

            /* 末尾 00 规则：末尾 N 字节改为 00，N = 半角 ASCII 数 */
            size_t ascii_cnt = _count_halfwidth_ascii(enc_data, (size_t)enc_len);
            if (ascii_cnt > 0 && ascii_cnt < DC_ROSTER_SLOT_SIZE)
                memset(decomp + slot_off + DC_ROSTER_SLOT_SIZE - ascii_cnt,
                       0x00, ascii_cnt);
        }

        Py_DECREF(encoded);
    }

    Py_DECREF(roster_extra);

    unsigned char *comp = _compress_block(decomp, decomp_size, out_comp_size);
    free(decomp);
    return comp;
}

/* ===================================================================
 * Python API: parse(data, extra=None, trans=None) -> dict
 * =================================================================== */

static PyObject *
dc_bin_parse(PyObject *self, PyObject *args, PyObject *kwargs)
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

    /* 验证大小 */
    if (data_size < DC_PTR_TABLE_SIZE)
    {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_ValueError, "DC.BIN: data too small");
        return NULL;
    }

    /* 读取指针 */
    uint32_t ptrs[DC_PTR_COUNT];
    for (int i = 0; i < DC_PTR_COUNT; i++)
        ptrs[i] = _read_le32(data + (size_t)i * 4);

    /* 验证首末指针 */
    if (ptrs[0] != DC_PTR_TABLE_SIZE || ptrs[DC_PTR_COUNT - 1] != (uint32_t)data_size)
    {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_ValueError,
                        "DC.BIN: invalid pointer table");
        return NULL;
    }

    int block_count = DC_PTR_COUNT - 1; /* 350 个块 */

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
                        "DC.BIN: failed to decompress block 0");
        return NULL;
    }

    PyObject *roster = _parse_roster(decomp, decomp_size, extra, trans);

    free(decomp);
    if (!roster)
    {
        PyBuffer_Release(&view);
        return NULL;
    }

    /* ===== 块 1~349: 角色详情 ===== */
    /* 确定有效角色数（名册条目数） */
    Py_ssize_t char_count = PyList_Size(roster);

    PyObject *dc_list = PyList_New(char_count);
    if (!dc_list)
    {
        Py_DECREF(roster);
        PyBuffer_Release(&view);
        return NULL;
    }

    for (int i = 0; i < char_count; i++)
    {
        size_t comp_start = ptrs[i + 1];
        size_t comp_end = ptrs[i + 2];
        size_t comp_size = comp_end - comp_start;

        decomp_size = 0;
        decomp = _decompress_block(data + comp_start, comp_size, &decomp_size);
        if (!decomp)
        {
            Py_DECREF(roster);
            Py_DECREF(dc_list);
            PyBuffer_Release(&view);
            PyErr_Format(PyExc_RuntimeError,
                         "DC.BIN: failed to decompress block %d", i + 1);
            return NULL;
        }

        PyObject *char_dict = _parse_character(decomp, decomp_size,
                                               extra, trans);
        free(decomp);

        if (!char_dict)
        {
            Py_DECREF(roster);
            Py_DECREF(dc_list);
            PyBuffer_Release(&view);
            return NULL;
        }

        PyList_SET_ITEM(dc_list, (Py_ssize_t)i, char_dict);
    }

    PyBuffer_Release(&view);

    /* 构建结果 */
    PyObject *result = PyDict_New();
    if (!result)
    {
        Py_DECREF(roster);
        Py_DECREF(dc_list);
        return NULL;
    }

    PyDict_SetItemString(result, "name", PyUnicode_FromString("dc"));
    PyDict_SetItemString(result, "count",
                         PyLong_FromSsize_t(char_count));
    PyDict_SetItemString(result, "roster", roster);
    PyDict_SetItemString(result, "dc", dc_list);

    Py_DECREF(roster);
    Py_DECREF(dc_list);
    return result;
}

/* ===================================================================
 * Python API: build(data, extra=None, trans=None) -> bytearray
 * =================================================================== */

static PyObject *
dc_bin_build(PyObject *self, PyObject *args, PyObject *kwargs)
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
                        "DC.BIN build: expected dict argument");
        return NULL;
    }

    /* 获取名册 */
    PyObject *roster = PyDict_GetItemString(data_dict, "roster");
    if (!roster || !PyList_Check(roster))
    {
        PyErr_SetString(PyExc_ValueError,
                        "DC.BIN build: 'roster' must be a list");
        return NULL;
    }

    /* 获取角色列表 */
    PyObject *dc_list = PyDict_GetItemString(data_dict, "dc");
    if (!dc_list || !PyList_Check(dc_list))
    {
        PyErr_SetString(PyExc_ValueError,
                        "DC.BIN build: 'dc' must be a list");
        return NULL;
    }

    Py_ssize_t char_count = PyList_Size(dc_list);
    Py_ssize_t roster_count = PyList_Size(roster);

    if (roster_count < char_count)
    {
        PyErr_SetString(PyExc_ValueError,
                        "DC.BIN build: roster count < character count");
        return NULL;
    }

    /* ===== 构建各块压缩数据 ===== */
    int block_count = (int)char_count + 1; /* +1 for roster block */
    unsigned char **comp_blocks = (unsigned char **)malloc(
        (size_t)block_count * sizeof(unsigned char *));
    size_t *comp_sizes = (size_t *)malloc((size_t)block_count * sizeof(size_t));

    if (!comp_blocks || !comp_sizes)
    {
        free(comp_blocks);
        free(comp_sizes);
        return NULL;
    }

    /* 块 0: 名册 — 从 roster 列表重建 */
    comp_blocks[0] = _build_roster(roster, (size_t)roster_count,
                                   extra, trans, &comp_sizes[0]);
    if (!comp_blocks[0])
    {
        free(comp_blocks);
        free(comp_sizes);
        return NULL;
    }

    /* 块 1~N: 角色详情 — 从字段数据重建 */
    for (Py_ssize_t i = 0; i < char_count; i++)
    {
        PyObject *char_dict = PyList_GetItem(dc_list, i);
        if (!char_dict || !PyDict_Check(char_dict))
        {
            PyErr_Format(PyExc_TypeError,
                         "DC.BIN build: dc[%d] must be a dict",
                         (int)i);
            for (Py_ssize_t j = 0; j <= i; j++)
                free(comp_blocks[j]);
            free(comp_blocks);
            free(comp_sizes);
            return NULL;
        }

        comp_blocks[i + 1] = _build_character(char_dict, extra, trans,
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

    /* ===== 计算总大小并拼接 ===== */
    size_t total_size = DC_PTR_TABLE_SIZE; /* 指针表 */
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

    /* 构建指针表 */
    size_t cur_offset = 0;
    for (int i = 0; i < block_count + 1; i++)
    {
        uint32_t ptr_value = DC_PTR_TABLE_SIZE + (uint32_t)cur_offset;
        _write_le32(output + (size_t)i * 4, ptr_value);
        if (i < block_count)
            cur_offset += comp_sizes[i];
    }

    /* 填充数据区 */
    unsigned char *data_ptr = output + DC_PTR_TABLE_SIZE;
    for (int i = 0; i < block_count; i++)
    {
        memcpy(data_ptr, comp_blocks[i], comp_sizes[i]);
        data_ptr += comp_sizes[i];
        free(comp_blocks[i]);
    }

    free(comp_blocks);
    free(comp_sizes);

    /* 转换为 Python bytearray */
    PyObject *result = PyByteArray_FromStringAndSize(
        (const char *)output, (Py_ssize_t)total_size);
    free(output);
    return result;
}

/* ===================================================================
 * 模块定义
 * =================================================================== */

static PyMethodDef dc_bin_methods[] = {
    {"parse", (PyCFunction)dc_bin_parse, METH_VARARGS | METH_KEYWORDS,
     "parse(data, extra=None, trans=None) -> dict\n\n"
     "Decompress and parse DC.BIN into a Python dict.\n"
     "Returns {name, count, roster, dc}."},
    {"build", (PyCFunction)dc_bin_build, METH_VARARGS | METH_KEYWORDS,
     "build(data, extra=None, trans=None) -> bytearray\n\n"
     "Build DC.BIN binary from a Python dict."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef dc_bin_module = {
    PyModuleDef_HEAD_INIT,
    "_dc_bin",
    "DC.BIN parser/builder for Super Robot Wars Alpha ROM Editor",
    -1,
    dc_bin_methods
};

PyMODINIT_FUNC
PyInit__dc_bin(void)
{
    return PyModule_Create(&dc_bin_module);
}
