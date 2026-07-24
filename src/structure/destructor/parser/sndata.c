#include "parser.h"

#define SP_QTY 0x200
#define BP_QTY 0x10
#define BP_LEN 0x4
#define s_count 0x8C
#define b_count 0xB
#define c_size 0x4000

#pragma pack(1)
typedef struct
{
    UINT8 code;
    UINT8 count;
    INT16 param[0];
} COMMAND;
typedef struct
{
    UINT32 区块数量;
    UINT32 索引长度;
    UINT32 区块索引[BP_QTY];
    char 指令数据[c_size];
} SCENARIO;
typedef struct
{
    UINT32 场景指针[SP_QTY];
    char 场景数据[0];
} SNDATA;
#pragma pack()

static PyObject *SNDATA_parse(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *BufByte;
    char *kw_list[] = {"buf", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Y", kw_list, &BufByte))
        return NULL;

    SNDATA *场景设计 = (SNDATA *)PyByteArray_AsString(BufByte);
    SCENARIO *场景 = (SCENARIO *)场景设计[0].场景数据;

    PyObject *SnDict = PyDict_New();
    PyObject *SnList = PyList_New(0);

    for (UINT16 s_idx = 0; s_idx < s_count; s_idx++)
    {
        PyObject *ScenarioDict = PyDict_New();
        PyDict_SetItem(ScenarioDict, Py_BuildValue("s", "Count"), Py_BuildValue("I", 场景[s_idx].区块数量));
        PyDict_SetItem(ScenarioDict, Py_BuildValue("s", "Width"), Py_BuildValue("I", 场景[s_idx].索引长度));

        PyObject *BlockList = PyList_New(0);
        for (UINT8 bp_idx = 0; bp_idx < BP_QTY; bp_idx++)
        {
            PyObject *BlockDict = PyDict_New();
            PyDict_SetItem(BlockDict, Py_BuildValue("s", "Index"), Py_BuildValue("I", 场景[s_idx].区块索引[bp_idx]));
            PyList_Append(BlockList, BlockDict);
        }
        PyDict_SetItem(ScenarioDict, Py_BuildValue("s", "Blocks"), BlockList);

        PyObject *CommandList = PyList_New(0);
        UINT16 offset = 0;
        while (场景[s_idx].指令数据[offset] != -1)
        {
            UINT8 length = 场景[s_idx].指令数据[offset + 1] * 2;
            char *command = (char *)calloc(length, sizeof(char));
            memcpy(command, 场景[s_idx].指令数据 + offset, length);
            COMMAND *指令 = (COMMAND *)command;

            PyObject *CommandDict = PyDict_New();
            PyDict_SetItem(CommandDict, Py_BuildValue("s", "Pos"), Py_BuildValue("H", offset / 2));
            PyDict_SetItem(CommandDict, Py_BuildValue("s", "Code"), Py_BuildValue("B", 指令[0].code));
            PyDict_SetItem(CommandDict, Py_BuildValue("s", "Count"), Py_BuildValue("B", 指令[0].count));

            PyObject *ParamList = PyList_New(0);
            if (指令[0].code == 0x64)
                PyList_Append(ParamList, Py_BuildValue("i", 指令[0].param[0] << 16 | (UINT16)指令[0].param[1]));
            else
            {
                for (UINT8 p_idx = 0; p_idx < (指令[0].count - 1); p_idx++)
                    PyList_Append(ParamList, Py_BuildValue("h", 指令[0].param[p_idx]));
            }
            PyDict_SetItem(CommandDict, Py_BuildValue("s", "Param"), ParamList);

            PyList_Append(CommandList, CommandDict);
            free(command);
            offset += length;
        }
        PyDict_SetItem(ScenarioDict, Py_BuildValue("s", "Commands"), CommandList);
        PyList_Append(SnList, ScenarioDict);
    }
    PyDict_SetItem(SnDict, Py_BuildValue("s", "场景设计"), SnList);

    return SnDict;
}

static PyObject *SNDATA_build(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *DataDict;
    char *kw_list[] = {"data", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O", kw_list, &DataDict))
        return NULL;

    PyObject *SnList = PyDict_GetItem(DataDict, Py_BuildValue("s", "场景设计"));

    SNDATA *场景设计 = (SNDATA *)malloc(sizeof(SNDATA) + sizeof(SCENARIO) * s_count);
    memset(场景设计, 0xFF, sizeof(SNDATA) + sizeof(SCENARIO) * s_count);
    memset(场景设计, 0x0, sizeof(SNDATA));

    UINT32 p_offset = SP_QTY * BP_LEN;
    for (UINT16 s_idx = 0; s_idx < s_count; s_idx++)
    {
        场景设计[0].场景指针[s_idx] = p_offset;

        PyObject *ScenarioDict = PyList_GetItem(SnList, s_idx);

        SCENARIO *场景 = (SCENARIO *)场景设计[0].场景数据;
        场景[s_idx].区块数量 = BP_QTY;
        场景[s_idx].索引长度 = BP_LEN;

        PyObject *CommandList = PyDict_GetItem(ScenarioDict, Py_BuildValue("s", "Commands"));
        UINT16 c_count = (UINT16)PyList_Size(CommandList);
        UINT32 s_offset = 0;
        for (UINT16 c_idx = 0; c_idx < c_count; c_idx++)
        {
            PyObject *CommandDict = PyList_GetItem(CommandList, c_idx);
            UINT8 code, count;
            PyArg_Parse(PyDict_GetItem(CommandDict, Py_BuildValue("s", "Code")), "B", &code);
            PyArg_Parse(PyDict_GetItem(CommandDict, Py_BuildValue("s", "Count")), "B", &count);

            PyObject *ParamList = PyDict_GetItem(CommandDict, Py_BuildValue("s", "Param"));
            if (code == 0x00)
            {
                UINT8 bp_idx;
                PyArg_Parse(PyList_GetItem(ParamList, 0), "h", &bp_idx);
                场景[s_idx].区块索引[bp_idx] = (UINT32)s_offset / 2;
            }

            场景[s_idx].指令数据[s_offset++] = code;
            场景[s_idx].指令数据[s_offset++] = count;
            if (code == 0x64)
            {
                UINT32 money;
                PyArg_Parse(PyList_GetItem(ParamList, 0), "i", &money);
                场景[s_idx].指令数据[s_offset++] = (money & 0xFF0000) >> 16;
                场景[s_idx].指令数据[s_offset++] = (money & 0xFF000000) >> 24;
                场景[s_idx].指令数据[s_offset++] = money & 0xFF;
                场景[s_idx].指令数据[s_offset++] = (money & 0xFF00) >> 8;
            }
            else
            {
                for (UINT8 p_idx = 0; p_idx < (count - 1); p_idx++)
                {
                    INT16 param;
                    PyArg_Parse(PyList_GetItem(ParamList, p_idx), "h", &param);
                    场景[s_idx].指令数据[s_offset++] = param & 0xFF;
                    场景[s_idx].指令数据[s_offset++] = (param & 0xFF00) >> 8;
                }
            }
        }
        p_offset += sizeof(SCENARIO);
    }
    场景设计[0].场景指针[s_count] = p_offset;

    PyObject *BufByte = PyByteArray_FromStringAndSize((char *)场景设计, sizeof(SNDATA) + sizeof(SCENARIO) * s_count);
    free(场景设计);

    return BufByte;
}

const char parse_doc[] = "parse(buf: bytearray) -> dict";
const char build_doc[] = "build(data: dict) -> bytearray";

static PyMethodDef SNDATAMethods[] =
    {
        {"parse", (PyCFunction)SNDATA_parse, METH_VARARGS | METH_KEYWORDS, parse_doc},
        {"build", (PyCFunction)SNDATA_build, METH_VARARGS | METH_KEYWORDS, build_doc},
        {NULL, NULL, 0, NULL}};

static struct PyModuleDef SNDATA_module =
    {
        PyModuleDef_HEAD_INIT,
        "SNDATA",
        "SNDATA.bin Parser",
        -1,
        SNDATAMethods};

PyMODINIT_FUNC PyInit_SNDATA(void)
{
    PyObject *module;
    module = PyModule_Create(&SNDATA_module);
    if (module == NULL)
        return NULL;
    return module;
}
