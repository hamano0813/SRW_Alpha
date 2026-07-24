#include "parser.h"

#pragma pack(1)
typedef struct
{
    char 文本[0x100];
} SNMSG;
#pragma pack()

static PyObject *SNMSG_parse(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *BufByte, *ExtraDict, *TransDict;
    char *kw_list[] = {"buf", "extra", "trans", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "YOO", kw_list, &BufByte, &ExtraDict, &TransDict))
        return NULL;

    PyObject *MsgList = PyList_New(0);
    UINT32 m_count = (UINT32)(PyByteArray_Size(BufByte) / sizeof(SNMSG));
    SNMSG *文本列表 = (SNMSG *)PyByteArray_AsString(BufByte);

    for (UINT32 m_idx = 0; m_idx < m_count; m_idx++)
    {
        PyObject *MsgDict = PyDict_New();
        PyDict_SetItem(MsgDict, Py_BuildValue("s", "文本"), decode(文本列表[m_idx].文本, ExtraDict, TransDict));
        PyList_Append(MsgList, MsgDict);
    }

    PyObject *DataDict = PyDict_New();
    PyDict_SetItem(DataDict, Py_BuildValue("s", "文本列表"), MsgList);

    return DataDict;
}

static PyObject *SNMSG_build(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *DataDict, *ExtraDict, *TransDict;
    char *kw_list[] = {"data", "extra", "trans", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OOO", kw_list, &DataDict, &ExtraDict, &TransDict))
        return NULL;

    PyObject *MsgList = PyDict_GetItem(DataDict, Py_BuildValue("s", "文本列表"));
    UINT32 m_count = (UINT32)PyList_Size(MsgList);
    SNMSG *文本列表 = (SNMSG *)calloc(m_count, sizeof(SNMSG));

    for (UINT32 m_idx = 0; m_idx < m_count; m_idx++)
    {
        PyObject *MsgDict = PyList_GetItem(MsgList, m_idx);
        strcpy(文本列表[m_idx].文本, encode(PyDict_GetItem(MsgDict, Py_BuildValue("s", "文本")), ExtraDict, TransDict));
    }

    PyObject *BufByte = PyByteArray_FromStringAndSize((char *)文本列表, sizeof(SNMSG) * m_count);
    free(文本列表);

    return BufByte;
}

const char parse_doc[] = "parse(buf: bytearray, extra: dict, trans: dict) -> dict";
const char build_doc[] = "build(data: dict, extra: dict, trans: dict) -> bytearray";

static PyMethodDef SNMSGMethods[] =
    {
        {"parse", (PyCFunction)SNMSG_parse, METH_VARARGS | METH_KEYWORDS, parse_doc},
        {"build", (PyCFunction)SNMSG_build, METH_VARARGS | METH_KEYWORDS, build_doc},
        {NULL, NULL, 0, NULL}};

static struct PyModuleDef SNMSG_module =
    {
        PyModuleDef_HEAD_INIT,
        "SNMSG",
        "SNMSG.bin Parser",
        -1,
        SNMSGMethods};

PyMODINIT_FUNC PyInit_SNMSG(void)
{
    PyObject *module;
    module = PyModule_Create(&SNMSG_module);
    if (module == NULL)
        return NULL;
    return module;
}
