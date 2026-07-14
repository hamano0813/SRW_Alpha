/*
 * snmsg_bin.c -- SNMSG.BIN parser/builder C extension
 *
 * SNMSG.BIN is a flat binary file (no LZSS compression) containing messages.
 * Each entry is exactly 0x100 bytes of shiftjisx0213-encoded text, 00-padded.
 * There is no file header, no mask residue — just consecutive fixed-length records.
 *
 * Python API (via _snmsg_bin.pyd):
 *   parse(data: bytearray | bytes, extra=None, trans=None) -> dict
 *   build(data: dict, extra=None, trans=None) -> bytearray
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "codec/codec.h"

/* 每条消息固定 256 字节 */
#define SNMSG_SZ 0x100

/* ===================================================================
 * Python API: parse
 *
 *   parse(data, extra=None, trans=None) -> dict
 *
 * 解析 SNMSG.BIN，每条消息解码为 str。
 * =================================================================== */

static PyObject *
snmsg_bin_parse(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"data", "extra", "trans", NULL};
    Py_buffer view;
    PyObject *extra = Py_None;
    PyObject *trans = Py_None;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y*|OO", (char **)kwlist,
                                     &view, &extra, &trans))
        return NULL;

    if (view.len == 0 || view.len % SNMSG_SZ != 0)
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_ValueError,
                     "SNMSG.BIN data size %zd is not a multiple of 0x100",
                     (size_t)view.len);
        return NULL;
    }

    size_t count = (size_t)view.len / SNMSG_SZ;

    PyObject *result = PyDict_New();
    if (!result)
    {
        PyBuffer_Release(&view);
        return NULL;
    }

    PyDict_SetItemString(result, "name", PyUnicode_FromString("snmsg"));
    PyDict_SetItemString(result, "count", PyLong_FromSize_t(count));

    PyObject *msgs_list = PyList_New((Py_ssize_t)count);
    if (!msgs_list)
    {
        Py_DECREF(result);
        PyBuffer_Release(&view);
        return NULL;
    }
    PyDict_SetItemString(result, "snmsgs", msgs_list);
    Py_DECREF(msgs_list);

    const unsigned char *ptr = (const unsigned char *)view.buf;
    for (size_t i = 0; i < count; i++)
    {
        PyObject *decoded = codec_decode((const char *)ptr, SNMSG_SZ, extra, trans);
        if (!decoded)
        {
            /* codec_decode already set the error */
            Py_DECREF(result);
            PyBuffer_Release(&view);
            return NULL;
        }
        PyList_SetItem(msgs_list, (Py_ssize_t)i, decoded);
        ptr += SNMSG_SZ;
    }

    PyBuffer_Release(&view);
    return result;
}

/* ===================================================================
 * Python API: build
 *
 *   build(data, extra=None, trans=None) -> bytearray
 *
 * 从 Python dict 重建 SNMSG.BIN 二进制。
 * 文本字段为 str 时经 codec.encode 编码，为 bytes 时直接写入。
 * 每条固定 0x100 字节，超出截断，不足 00 填充。
 * =================================================================== */

static PyObject *
snmsg_bin_build(PyObject *self, PyObject *args, PyObject *kwargs)
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
    Py_ssize_t count = PyLong_AsSsize_t(py_count);

    PyObject *py_msgs = PyDict_GetItemString(py_dict, "snmsgs");
    if (!py_msgs || !PyList_Check(py_msgs))
    {
        PyErr_SetString(PyExc_KeyError, "Missing or invalid 'snmsgs'");
        return NULL;
    }
    if (count != PyList_Size(py_msgs))
    {
        PyErr_SetString(PyExc_ValueError,
                        "'snmsgs' list size does not match 'count'");
        return NULL;
    }

    /* 空列表 */
    if (count == 0)
    {
        return PyByteArray_FromStringAndSize("", 0);
    }

    size_t out_len = (size_t)count * SNMSG_SZ;
    unsigned char *raw = (unsigned char *)calloc(out_len, 1);
    if (!raw)
        return PyErr_NoMemory();

    unsigned char *ptr = raw;
    for (Py_ssize_t i = 0; i < count; i++)
    {
        PyObject *item = PyList_GetItem(py_msgs, i);
        if (!item)
        {
            free(raw);
            PyErr_SetString(PyExc_TypeError, "Failed to get list item");
            return NULL;
        }

        if (PyUnicode_Check(item))
        {
            if (PyUnicode_GET_LENGTH(item) == 0)
            {
                ptr += SNMSG_SZ;
                continue;
            }

            PyObject *enc = codec_encode(item, extra, trans);
            if (!enc)
            {
                free(raw);
                return NULL;
            }

            char *buf;
            Py_ssize_t len;
            if (PyBytes_AsStringAndSize(enc, &buf, &len) == -1)
            {
                Py_DECREF(enc);
                free(raw);
                return NULL;
            }

            /* 超出 0x100 的部分截断 */
            Py_ssize_t copy_len = len < SNMSG_SZ ? len : SNMSG_SZ;
            memcpy(ptr, buf, (size_t)copy_len);
            Py_DECREF(enc);
        }
        else if (PyBytes_Check(item))
        {
            char *buf;
            Py_ssize_t len;
            if (PyBytes_AsStringAndSize(item, &buf, &len) == -1)
            {
                free(raw);
                return NULL;
            }
            Py_ssize_t copy_len = len < SNMSG_SZ ? len : SNMSG_SZ;
            memcpy(ptr, buf, (size_t)copy_len);
        }

        ptr += SNMSG_SZ;
    }

    PyObject *result = PyByteArray_FromStringAndSize((char *)raw, (Py_ssize_t)out_len);
    free(raw);
    return result;
}

/* ===================================================================
 * 模块方法表
 * =================================================================== */

static PyMethodDef SnmsgBinMethods[] = {
    {"parse", (PyCFunction)snmsg_bin_parse, METH_VARARGS | METH_KEYWORDS,
     "Parse SNMSG.BIN data into a Python dict."},
    {"build", (PyCFunction)snmsg_bin_build, METH_VARARGS | METH_KEYWORDS,
     "Build SNMSG.BIN binary data from a Python dict."},
    {NULL, NULL, 0, NULL}  /* sentinel */
};

/* ===================================================================
 * 模块定义
 * =================================================================== */

static struct PyModuleDef snmsgbin_module = {
    PyModuleDef_HEAD_INIT,
    "_snmsg_bin",
    "SNMSG.BIN parser/builder",
    -1,
    SnmsgBinMethods,
};

/* ===================================================================
 * 模块入口
 * =================================================================== */

PyMODINIT_FUNC PyInit__snmsg_bin(void) {
    return PyModule_Create(&snmsgbin_module);
}
