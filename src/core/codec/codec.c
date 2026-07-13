/*
 * codec — Shift-JIS x0213 文本编解码 C 扩展
 *
 * 为《超级机器人大战α》ROM Editor 提供文本编解码功能。
 * 支持定长文本（掩码覆写）与不定长文本两种模式。
 *
 * 两种编译模式：
 *   - 独立模块：编译为 _codec.pyd（默认）
 *   - 子模块：   定义 CODEC_AS_SUBMODULE 后链接到其他 C 扩展
 *                （跳过 PyInit__codec，函数名不冲突）
 *
 * Python API（通过 _codec.pyd 导出）：
 *   decode(data, extra=None, trans=None)                          -> str
 *   encode(text, mask, extra=None, trans=None)                    -> bytearray
 *   encode_var(text, extra=None, trans=None)                      -> (bytes, int)
 *
 * C 内部 API（供 robot_raf.c 等调用）：
 *   codec_decode(s, len, extra, trans)                            -> PyObject* (str)
 *   codec_encode(text, extra, trans)                              -> PyObject* (bytes)
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <string.h>

/* ===================================================================
 * 字典辅助函数（纯 C 实现）
 *
 * _dict_to_sorted_items(dict)  -> list[tuple[str,str]]  按键长降序
 * _build_reverse_dict(dict)    -> dict[str,str]         值→键，重复取最长键
 * =================================================================== */

/* 将映射字典转为按键长降序排列的 (键, 值) 列表 */
static PyObject *_dict_to_sorted_items(PyObject *dict)
{
    if (!dict || dict == Py_None || PyDict_Size(dict) == 0)
        return PyList_New(0);

    PyObject *items = PyDict_Items(dict);
    if (!items)
        return NULL;

    Py_ssize_t n = PyList_Size(items);
    if (n <= 1)
        return items;

    /* 包装为 (负键长, 键, 值) 三元组 → 排序后拆包 */
    PyObject *wrapped = PyList_New(n);
    if (!wrapped)
    {
        Py_DECREF(items);
        return NULL;
    }

    for (Py_ssize_t i = 0; i < n; i++)
    {
        PyObject *item = PyList_GET_ITEM(items, i);
        PyObject *key = PyTuple_GET_ITEM(item, 0);
        PyObject *val = PyTuple_GET_ITEM(item, 1);

        PyObject *neg_len = PyLong_FromSsize_t(-PyUnicode_GET_LENGTH(key));
        if (!neg_len)
        {
            Py_DECREF(items);
            Py_DECREF(wrapped);
            return NULL;
        }

        PyObject *triple = PyTuple_Pack(3, neg_len, key, val);
        Py_DECREF(neg_len);
        if (!triple)
        {
            Py_DECREF(items);
            Py_DECREF(wrapped);
            return NULL;
        }

        PyList_SET_ITEM(wrapped, i, triple);
    }

    Py_DECREF(items);

    /* 排序：负键长升序 = 正键长降序 */
    if (PyList_Sort(wrapped) < 0)
    {
        Py_DECREF(wrapped);
        return NULL;
    }

    /* 拆包回 (键, 值) 对 */
    PyObject *result = PyList_New(n);
    if (!result)
    {
        Py_DECREF(wrapped);
        return NULL;
    }

    for (Py_ssize_t i = 0; i < n; i++)
    {
        PyObject *triple = PyList_GET_ITEM(wrapped, i);
        PyObject *key = PyTuple_GET_ITEM(triple, 1);
        PyObject *val = PyTuple_GET_ITEM(triple, 2);
        Py_INCREF(key);
        Py_INCREF(val);
        PyObject *pair = PyTuple_Pack(2, key, val);
        Py_DECREF(key);
        Py_DECREF(val);
        if (!pair)
        {
            Py_DECREF(wrapped);
            Py_DECREF(result);
            return NULL;
        }
        PyList_SET_ITEM(result, i, pair);
    }

    Py_DECREF(wrapped);
    return result;
}

/* 构建反向映射（值→键），重复值时保留最长键 */
static PyObject *_build_reverse_dict(PyObject *dict)
{
    if (!dict || dict == Py_None || PyDict_Size(dict) == 0)
        return PyDict_New();

    PyObject *result = PyDict_New();
    if (!result)
        return NULL;

    PyObject *items = PyDict_Items(dict);
    if (!items)
    {
        Py_DECREF(result);
        return NULL;
    }

    Py_ssize_t n = PyList_Size(items);
    for (Py_ssize_t i = 0; i < n; i++)
    {
        PyObject *item = PyList_GET_ITEM(items, i);
        PyObject *key = PyTuple_GET_ITEM(item, 0); /* 原键 → 将成为反向值 */
        PyObject *val = PyTuple_GET_ITEM(item, 1); /* 原值 → 将成为反向键 */

        /* 值重复时，只保留最长键 */
        PyObject *existing = PyDict_GetItem(result, val); /* borrowed */
        if (existing)
        {
            if (PyUnicode_GET_LENGTH(key) <= PyUnicode_GET_LENGTH(existing))
                continue;
        }

        if (PyDict_SetItem(result, val, key) < 0)
        {
            Py_DECREF(items);
            Py_DECREF(result);
            return NULL;
        }
    }

    Py_DECREF(items);
    return result;
}

/* ===================================================================
 * _map_apply_impl — 扫描式文本替换
 *
 * 从左到右逐位置扫描，在每个位置优先匹配最长的键。
 * 匹配成功后跳过已匹配区域，不回溯替换后的文本。
 * items 必须是按键长降序排列的 (键, 值) 列表。
 *
 * Returns: new reference to str, or NULL on error.
 * =================================================================== */

static PyObject *_map_apply_impl(PyObject *text, PyObject *items)
{
    if (!PyUnicode_Check(text))
    {
        PyErr_SetString(PyExc_TypeError, "Expected a str for text");
        return NULL;
    }
    if (!PyList_Check(items))
    {
        PyErr_SetString(PyExc_TypeError, "Expected a list for items");
        return NULL;
    }

    Py_ssize_t text_len = PyUnicode_GET_LENGTH(text);
    Py_ssize_t item_cnt = PyList_GET_SIZE(items);

    if (text_len == 0 || item_cnt == 0)
    {
        Py_INCREF(text);
        return text;
    }

    PyObject *chunks = PyList_New(0);
    if (!chunks)
        return NULL;

    Py_ssize_t pos = 0;
    while (pos < text_len)
    {
        int matched = 0;

        for (Py_ssize_t i = 0; i < item_cnt; i++)
        {
            PyObject *pair = PyList_GET_ITEM(items, i);
            if (!PyTuple_Check(pair) || PyTuple_GET_SIZE(pair) != 2)
                continue;

            PyObject *key = PyTuple_GET_ITEM(pair, 0);
            PyObject *value = PyTuple_GET_ITEM(pair, 1);

            if (!PyUnicode_Check(key) || !PyUnicode_Check(value))
                continue;

            Py_ssize_t key_len = PyUnicode_GET_LENGTH(key);
            if (pos + key_len > text_len)
                continue;

            int match = 1;
            for (Py_ssize_t k = 0; k < key_len; k++)
            {
                if (PyUnicode_READ_CHAR(text, pos + k) !=
                    PyUnicode_READ_CHAR(key, k))
                {
                    match = 0;
                    break;
                }
            }

            if (match)
            {
                if (PyList_Append(chunks, value) < 0)
                {
                    Py_DECREF(chunks);
                    return NULL;
                }
                pos += key_len;
                matched = 1;
                break;
            }
        }

        if (!matched)
        {
            Py_UCS4 ch = PyUnicode_READ_CHAR(text, pos);
            PyObject *ch_str = PyUnicode_FromOrdinal(ch);
            if (!ch_str)
            {
                Py_DECREF(chunks);
                return NULL;
            }
            if (PyList_Append(chunks, ch_str) < 0)
            {
                Py_DECREF(ch_str);
                Py_DECREF(chunks);
                return NULL;
            }
            Py_DECREF(ch_str);
            pos += 1;
        }
    }

    PyObject *sep = PyUnicode_New(0, 0x80);
    if (!sep)
    {
        Py_DECREF(chunks);
        return NULL;
    }
    PyObject *result = PyUnicode_Join(sep, chunks);
    Py_DECREF(sep);
    Py_DECREF(chunks);
    return result;
}

/* ===================================================================
 * C 内部 API：codec_decode
 *
 * 将 Shift-JIS x0213 字节解码为 Python str。
 * 按顺序：读取到 0x00 截断 → shift_jisx0213 解码 → extra → trans。
 *
 * Parameters:
 *   s     — 字节数据指针
 *   len   — 缓冲区大小上限（防止越界）
 *   extra — dict[str,str] 或 NULL（游戏冷僻字 → 显示文本）
 *   trans — dict[str,str] 或 NULL（用户自定义替换）
 *
 * Returns: new reference to Python str, or NULL on error.
 * =================================================================== */

PyObject *codec_decode(const char *s, size_t len,
                       PyObject *extra, PyObject *trans)
{
    /* 读到 0x00 截断 */
    size_t text_len = 0;
    while (text_len < len && s[text_len] != 0x00)
        text_len++;

    /* shift_jisx0213 解码 */
    PyObject *str = PyUnicode_Decode(s, (Py_ssize_t)text_len,
                                     "shift_jisx0213", "replace");
    if (!str)
        return NULL;

    /* 应用 extra（游戏内码 → 显示文本） */
    if (extra && extra != Py_None && PyDict_Size(extra) > 0)
    {
        PyObject *items = _dict_to_sorted_items(extra);
        if (!items)
        {
            Py_DECREF(str);
            return NULL;
        }
        PyObject *tmp = _map_apply_impl(str, items);
        Py_DECREF(str);
        Py_DECREF(items);
        str = tmp;
        if (!str)
            return NULL;
    }

    /* 应用 trans（用户自定义替换） */
    if (trans && trans != Py_None && PyDict_Size(trans) > 0)
    {
        PyObject *items = _dict_to_sorted_items(trans);
        if (!items)
        {
            Py_DECREF(str);
            return NULL;
        }
        PyObject *tmp = _map_apply_impl(str, items);
        Py_DECREF(str);
        Py_DECREF(items);
        str = tmp;
    }

    return str;
}

/* ===================================================================
 * C 内部 API：codec_encode
 *
 * 将 Python str 编码为 Shift-JIS x0213 字节。
 * 按顺序：trans_rev → extra_rev → shift_jisx0213 编码。
 *
 * Parameters:
 *   text  — Python str
 *   extra — dict[str,str] 或 NULL
 *   trans — dict[str,str] 或 NULL
 *
 * Returns: new reference to Python bytes（不含 0x00 终结符），
 *          或 NULL on error。
 * =================================================================== */

PyObject *codec_encode(PyObject *text, PyObject *extra, PyObject *trans)
{
    PyObject *str = text;
    Py_INCREF(str);

    /* 应用 trans 反向（用户文本 → 显示文本） */
    if (trans && trans != Py_None && PyDict_Size(trans) > 0)
    {
        PyObject *rev = _build_reverse_dict(trans);
        if (!rev)
        {
            Py_DECREF(str);
            return NULL;
        }
        PyObject *items = _dict_to_sorted_items(rev);
        Py_DECREF(rev);
        if (!items)
        {
            Py_DECREF(str);
            return NULL;
        }
        PyObject *tmp = _map_apply_impl(str, items);
        Py_DECREF(str);
        Py_DECREF(items);
        str = tmp;
        if (!str)
            return NULL;
    }

    /* 应用 extra 反向（显示文本 → 游戏内码） */
    if (extra && extra != Py_None && PyDict_Size(extra) > 0)
    {
        PyObject *rev = _build_reverse_dict(extra);
        if (!rev)
        {
            Py_DECREF(str);
            return NULL;
        }
        PyObject *items = _dict_to_sorted_items(rev);
        Py_DECREF(rev);
        if (!items)
        {
            Py_DECREF(str);
            return NULL;
        }
        PyObject *tmp = _map_apply_impl(str, items);
        Py_DECREF(str);
        Py_DECREF(items);
        str = tmp;
        if (!str)
            return NULL;
    }

    /* Shift-JIS x0213 编码 */
    PyObject *result = PyUnicode_AsEncodedString(str,
                                                 "shift_jisx0213", "replace");
    Py_DECREF(str);
    return result;
}

/* ===================================================================
 * Python 封装：decode(data, extra=None, trans=None) -> str
 *
 * 从字节数据中解码文本。
 * data 可以是 bytes 或 bytearray。
 * =================================================================== */

static PyObject *py_decode(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"data", "extra", "trans", NULL};
    Py_buffer view;
    PyObject *extra = Py_None;
    PyObject *trans = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y*|OO", (char **)kwlist,
                                     &view, &extra, &trans))
        return NULL;

    PyObject *result = codec_decode(
        (const char *)view.buf, (size_t)view.len, extra, trans);

    PyBuffer_Release(&view);
    return result;
}

/* ===================================================================
 * Python 封装：encode(text, mask, extra=None, trans=None) -> bytearray
 *
 * 定长文本编码。在 mask 副本上覆写 Shift-JIS 编码 + 0x00 终结。
 * mask 不可省略，其长度决定输出缓冲区大小。
 * 编码后文本 + 0x00 超出 mask 长度时抛出 ValueError。
 * =================================================================== */

static PyObject *py_encode(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"text", "mask", "extra", "trans", NULL};
    PyObject *text_obj;
    Py_buffer mask_view;
    PyObject *extra = Py_None;
    PyObject *trans = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Oy*|OO", (char **)kwlist,
                                     &text_obj, &mask_view, &extra, &trans))
        return NULL;

    if (!PyUnicode_Check(text_obj))
    {
        PyBuffer_Release(&mask_view);
        PyErr_SetString(PyExc_TypeError, "Expected a str for text");
        return NULL;
    }

    /* 编码文本（反向映射 + shift_jisx0213） */
    PyObject *encoded = codec_encode(text_obj, extra, trans);
    if (!encoded)
    {
        PyBuffer_Release(&mask_view);
        return NULL;
    }

    Py_ssize_t enc_len = PyBytes_GET_SIZE(encoded);
    int mask_len = (int)mask_view.len;

    /* 检查是否超出掩码缓冲区（需留 1 字节给 0x00 终结符） */
    if (enc_len + 1 > mask_len)
    {
        PyBuffer_Release(&mask_view);
        PyErr_Format(PyExc_ValueError,
                     "Encoded text too long (%zd bytes + null) "
                     "for mask buffer size %d",
                     enc_len, mask_len);
        Py_DECREF(encoded);
        return NULL;
    }

    /* 复制掩码，覆写文本 + 0x00 */
    PyObject *result = PyByteArray_FromStringAndSize(
        (const char *)mask_view.buf, (Py_ssize_t)mask_len);
    if (!result)
    {
        PyBuffer_Release(&mask_view);
        Py_DECREF(encoded);
        return NULL;
    }

    unsigned char *buf = (unsigned char *)PyByteArray_AsString(result);
    memcpy(buf, PyBytes_AS_STRING(encoded), (size_t)enc_len);
    buf[enc_len] = 0x00;

    PyBuffer_Release(&mask_view);
    Py_DECREF(encoded);
    return result;
}

/* ===================================================================
 * Python 封装：encode_var(text, extra=None, trans=None) -> (bytes, int)
 *
 * 不定长文本编码。
 * 返回 (含 0x00 终结的字节串, 总长度)。
 * 总长度 = len(bytes)（已包含最后的 0x00）。
 * =================================================================== */

static PyObject *py_encode_var(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"text", "extra", "trans", NULL};
    PyObject *text_obj;
    PyObject *extra = Py_None;
    PyObject *trans = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|OO", (char **)kwlist,
                                     &text_obj, &extra, &trans))
        return NULL;

    if (!PyUnicode_Check(text_obj))
    {
        PyErr_SetString(PyExc_TypeError, "Expected a str for text");
        return NULL;
    }

    /* 编码文本 */
    PyObject *encoded = codec_encode(text_obj, extra, trans);
    if (!encoded)
        return NULL;

    Py_ssize_t enc_len = PyBytes_GET_SIZE(encoded);

    /* 构建含 0x00 终结的字节串 */
    PyObject *result_bytes = PyBytes_FromStringAndSize(NULL, enc_len + 1);
    if (!result_bytes)
    {
        Py_DECREF(encoded);
        return NULL;
    }

    memcpy(PyBytes_AS_STRING(result_bytes),
           PyBytes_AS_STRING(encoded), (size_t)enc_len);
    PyBytes_AS_STRING(result_bytes)[enc_len] = 0x00;

    Py_DECREF(encoded);

    /* 打包为 (bytes, int) 元组 */
    PyObject *length = PyLong_FromSsize_t(enc_len + 1);
    if (!length)
    {
        Py_DECREF(result_bytes);
        return NULL;
    }

    PyObject *tuple = PyTuple_Pack(2, result_bytes, length);
    Py_DECREF(result_bytes);
    Py_DECREF(length);
    return tuple;
}

/* ===================================================================
 * 模块方法表
 * =================================================================== */

static PyMethodDef CodecMethods[] = {
    {"decode", (PyCFunction)py_decode, METH_VARARGS | METH_KEYWORDS,
     "decode(data, extra=None, trans=None) -> str\n"
     "Decode Shift-JIS x0213 bytes to text.\n"
     "Reads until 0x00, decodes as shift_jisx0213, then applies\n"
     "extra and trans mappings in that order."},
    {"encode", (PyCFunction)py_encode, METH_VARARGS | METH_KEYWORDS,
     "encode(text, mask, extra=None, trans=None) -> bytearray\n"
     "Fixed-length text encoding.\n"
     "Overlays Shift-JIS encoded text + 0x00 onto a copy of mask."},
    {"encode_var", (PyCFunction)py_encode_var, METH_VARARGS | METH_KEYWORDS,
     "encode_var(text, extra=None, trans=None) -> (bytes, int)\n"
     "Variable-length text encoding.\n"
     "Returns (encoded_bytes_with_null, total_length)."},
    {NULL, NULL, 0, NULL}};

/* ===================================================================
 * 模块初始化（独立编译模式）
 * =================================================================== */

#ifndef CODEC_AS_SUBMODULE

static struct PyModuleDef codec_module = {
    PyModuleDef_HEAD_INIT,
    "_codec",
    "Shift-JIS x0213 text codec for Super Robot Wars Alpha ROM Editor.",
    -1,
    CodecMethods};

PyMODINIT_FUNC PyInit__codec(void)
{
    return PyModule_Create(&codec_module);
}

#endif /* !CODEC_AS_SUBMODULE */
