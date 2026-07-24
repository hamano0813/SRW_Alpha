#include "parser.h"

#define SP_COUNT 0xFF

UINT16 roundup(UINT32 number, UINT32 digit)
{
    return ((number + digit - 1) / digit) * digit;
}

PyObject *SCRIPT_parse(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *BufByte, *ExtraDict, *TransDict;
    char *kw_list[] = {"buf", "extra", "trans", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "YOO", kw_list, &BufByte, &ExtraDict, &TransDict))
        return NULL;

    unsigned char *buffer = (char *)PyByteArray_AsString(BufByte);
    PyObject *ScriptDict = PyDict_New();

    PyObject *ScreenList = PyList_New(0);
    UINT32 p_offset = 0x0;

    for (UINT32 p_idx = 0; p_idx < (SP_COUNT - 1); p_idx++)
    {

        UINT32 c_offset = buffer[p_offset] | buffer[p_offset + 1] << 8 | buffer[p_offset + 2] << 16 | buffer[p_offset + 3] << 24;
        p_offset += 0x4;
        UINT32 c_count = buffer[c_offset] | buffer[c_offset + 1] << 8 | buffer[c_offset + 2] << 16 | buffer[c_offset + 3] << 24;
        c_offset += 0x4;

        PyObject *ScreenDict = PyDict_New();
        PyObject *CommandList = PyList_New(0);
        for (UINT32 c_idx = 0; c_idx < c_count; c_idx++)
        {
            UINT16 code = buffer[c_offset + 0] | buffer[c_offset + 1] << 8;
            UINT16 param1 = buffer[c_offset + 2] | buffer[c_offset + 3] << 8;
            UINT16 param2 = buffer[c_offset + 4] | buffer[c_offset + 5] << 8;
            UINT16 expand = buffer[c_offset + 6] | buffer[c_offset + 7] << 8;
            c_offset += 8;
            PyObject *CommandDict = PyDict_New();

            PyDict_SetItem(CommandDict, Py_BuildValue("s", "指令码"), Py_BuildValue("H", code));
            PyDict_SetItem(CommandDict, Py_BuildValue("s", "参数一"), Py_BuildValue("H", param1));
            PyDict_SetItem(CommandDict, Py_BuildValue("s", "参数二"), Py_BuildValue("H", param2));
            PyDict_SetItem(CommandDict, Py_BuildValue("s", "扩展字节"), Py_BuildValue("H", expand));
            if (expand > 0)
            {
                char *str = (char *)calloc(expand, 1);
                memcpy(str, buffer + c_offset, (size_t)expand);
                PyDict_SetItem(CommandDict, Py_BuildValue("s", "扩展文本"), decode(str, ExtraDict, TransDict));
                free(str);
                c_offset += roundup(expand, 0x4);
            }
            else
                PyDict_SetItem(CommandDict, Py_BuildValue("s", "扩展文本"), Py_BuildValue("s", ""));
            PyList_Append(CommandList, CommandDict);
        }
        PyDict_SetItem(ScreenDict, Py_BuildValue("s", "指令列表"), CommandList);
        PyList_Append(ScreenList, ScreenDict);
    }
    PyDict_SetItem(ScriptDict, Py_BuildValue("s", "剧本列表"), ScreenList);
    return ScriptDict;
}

PyObject *SCRIPT_build(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *DataDict, *ExtraDict, *TransDict;
    char *kw_list[] = {"data", "extra", "trans", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OOO", kw_list, &DataDict, &ExtraDict, &TransDict))
        return NULL;

    UINT32 p_offset = 0;
    UINT32 c_offset = SP_COUNT * 0x4;
    unsigned char *buffer = (char *)calloc(0x7FFFFF, 1);
    char completion[3] = {0x00, 0xD4, 0x41};

    PyObject *ScreenList = PyDict_GetItem(DataDict, Py_BuildValue("s", "剧本列表"));

    for (UINT32 p_idx = 0; p_idx < (SP_COUNT - 1); p_idx++)
    {
        buffer[p_offset++] = c_offset & 0xFF;
        buffer[p_offset++] = c_offset >> 8 & 0xFF;
        buffer[p_offset++] = c_offset >> 16 & 0xFF;
        buffer[p_offset++] = c_offset >> 24 & 0xFF;

        PyObject *ScreenDict = PyList_GetItem(ScreenList, p_idx);
        PyObject *CommandList = PyDict_GetItem(ScreenDict, Py_BuildValue("s", "指令列表"));

        UINT32 c_count = (UINT32)PyList_Size(CommandList);

        buffer[c_offset++] = c_count & 0xFF;
        buffer[c_offset++] = c_count >> 8 & 0xFF;
        buffer[c_offset++] = c_count >> 16 & 0xFF;
        buffer[c_offset++] = c_count >> 24 & 0xFF;

        UINT16 code, param1, param2, expand;
        for (UINT32 c_idx = 0; c_idx < c_count; c_idx++)
        {
            PyObject *CommandDict = PyList_GetItem(CommandList, c_idx);
            PyArg_Parse(PyDict_GetItem(CommandDict, Py_BuildValue("s", "指令码")), "H", &code);
            PyArg_Parse(PyDict_GetItem(CommandDict, Py_BuildValue("s", "参数一")), "H", &param1);
            PyArg_Parse(PyDict_GetItem(CommandDict, Py_BuildValue("s", "参数二")), "H", &param2);
            char *str = encode(PyDict_GetItem(CommandDict, Py_BuildValue("s", "扩展文本")), ExtraDict, TransDict);
            expand = (UINT16)strlen(str);
            if (expand > 1)
                expand += 1;
            else
                PyArg_Parse(PyDict_GetItem(CommandDict, Py_BuildValue("s", "扩展字节")), "H", &expand);
            buffer[c_offset++] = code & 0xFF;
            buffer[c_offset++] = code >> 8 & 0xFF;
            buffer[c_offset++] = param1 & 0xFF;
            buffer[c_offset++] = param1 >> 8 & 0xFF;
            buffer[c_offset++] = param2 & 0xFF;
            buffer[c_offset++] = param2 >> 8 & 0xFF;
            buffer[c_offset++] = expand & 0xFF;
            buffer[c_offset++] = expand >> 8 & 0xFF;
            if (expand > 0)
            {
                memcpy(buffer + c_offset, str, expand - 1);
                buffer[c_offset + expand] = 0;
                c_offset += expand;
                UINT8 com_len = roundup(expand, 0x4) - expand;
                if (com_len > 0)
                {
                    memcpy(buffer + c_offset, completion, com_len);
                    c_offset += com_len;
                }
            }
        }
    }
    buffer[p_offset++] = c_offset & 0xFF;
    buffer[p_offset++] = c_offset >> 8 & 0xFF;
    buffer[p_offset++] = c_offset >> 16 & 0xFF;
    buffer[p_offset++] = c_offset >> 24 & 0xFF;

    PyObject *BufByte = PyByteArray_FromStringAndSize(buffer, c_offset);
    free(buffer);
    return BufByte;
}

const char parse_doc[] = "parse(buf: bytearray, extra: dict, trans: dict) -> dict";
const char build_doc[] = "build(data: dict, extra: dict, trans: dict) -> bytearray";

static PyMethodDef SCRIPTMethods[] =
    {
        {"parse", (PyCFunction)SCRIPT_parse, METH_VARARGS | METH_KEYWORDS, parse_doc},
        {"build", (PyCFunction)SCRIPT_build, METH_VARARGS | METH_KEYWORDS, build_doc},
        {NULL, NULL, 0, NULL}};

static struct PyModuleDef SCRIPT_module =
    {
        PyModuleDef_HEAD_INIT,
        "SCRIPT",
        "SCRIPT.bin Parser",
        -1,
        SCRIPTMethods};

PyMODINIT_FUNC PyInit_SCRIPT(void)
{
    PyObject *module;
    module = PyModule_Create(&SCRIPT_module);
    if (module == NULL)
        return NULL;
    return module;
}
