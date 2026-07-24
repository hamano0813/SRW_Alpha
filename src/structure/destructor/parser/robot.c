#include "parser.h"

#pragma pack(1)
typedef struct
{
    UINT8 代码 : 4;
    UINT8 新人类 : 2;
    UINT8 圣战士 : 2;
    UINT8 气力;
    UINT8 改造类型 : 2;
    UINT8 近射程 : 2;
    UINT8 远射程 : 4;
    UINT8 地图武器分类 : 2;
    UINT8 着弹点指定型攻击半径 : 3;
    UINT8 : 3;
    UINT16 攻击力;
    UINT8 分类 : 1;
    UINT8 属性 : 7;
    UINT8 : 4;
    UINT8 改造追加 : 4;
    char 武器[0x15];
    UINT8 方向指定型范围;
    UINT8 地图武器演出;
    UINT8 ＥＮ;
    INT8 命中;
    INT8 ＣＴ;
    UINT8 初期弹数;
    UINT8 最大弹数;
    UINT8 空适应;
    UINT8 陆适应;
    UINT8 海适应;
    UINT8 宇适应;
} WEAPON;
typedef struct
{
    char 机体[0x1A];
    UINT16 代码;
    UINT8 移动类型 : 4;
    UINT8 : 4;
    UINT8 移动力;
    UINT16 ＨＰ;
    UINT16 ＥＮ;
    UINT16 运动性;
    UINT16 装甲;
    UINT16 限界;
    UINT8 体积;
    UINT8 芯片;
    UINT16 换乘系 : 10;
    UINT16 : 6;
    UINT32 特性 : 31;
    UINT32 : 1;
    UINT16 修理费;
    UINT16 资金;
    UINT8 变形组号;
    UINT8 变形序号;
    UINT8 合体组号;
    UINT8 合体序号;
    UINT16 分离机体;
    UINT8 合体数;
    UINT8 换装系统;
    UINT8 机体BGM;
    UINT8 : 8;
    UINT8 : 8;
    UINT8 : 8;
    UINT8 空适应;
    UINT8 陆适应;
    UINT8 海适应;
    UINT8 宇适应;
    WEAPON 武器列表[0x10];
} ROBOT;
#pragma pack()

static PyObject *ROBOT_parse(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *BufByte, *ExtraDict, *TransDict;
    char *kw_list[] = {"buffer", "extra", "trans", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "YOO", kw_list, &BufByte, &ExtraDict, &TransDict))
        return NULL;

    UINT16 r_count = (UINT16)(PyByteArray_Size(BufByte) / sizeof(ROBOT));
    UINT8 w_count = 0x10;

    ROBOT *机体列表 = (ROBOT *)PyByteArray_AsString(BufByte);

    PyObject *RobotList = PyList_New(0);

    for (UINT16 r_idx = 0; r_idx < r_count; r_idx++)
    {
        PyObject *RobotDict = PyDict_New();

        PyDict_SetItem(RobotDict, Py_BuildValue("s", "机体"), decode(机体列表[r_idx].机体, ExtraDict, TransDict));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "代码"), Py_BuildValue("i", 机体列表[r_idx].代码));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "移动类型"), Py_BuildValue("i", 机体列表[r_idx].移动类型));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "移动力"), Py_BuildValue("i", 机体列表[r_idx].移动力));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "ＨＰ"), Py_BuildValue("i", 机体列表[r_idx].ＨＰ));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "ＥＮ"), Py_BuildValue("i", 机体列表[r_idx].ＥＮ));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "运动性"), Py_BuildValue("i", 机体列表[r_idx].运动性));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "装甲"), Py_BuildValue("i", 机体列表[r_idx].装甲));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "限界"), Py_BuildValue("i", 机体列表[r_idx].限界));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "体积"), Py_BuildValue("i", 机体列表[r_idx].体积));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "芯片"), Py_BuildValue("i", 机体列表[r_idx].芯片));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "换乘系"), Py_BuildValue("i", 机体列表[r_idx].换乘系));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "特性"), Py_BuildValue("i", 机体列表[r_idx].特性));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "修理费"), Py_BuildValue("i", 机体列表[r_idx].修理费));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "资金"), Py_BuildValue("i", 机体列表[r_idx].资金));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "变形组号"), Py_BuildValue("i", 机体列表[r_idx].变形组号));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "变形序号"), Py_BuildValue("i", 机体列表[r_idx].变形序号));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "合体组号"), Py_BuildValue("i", 机体列表[r_idx].合体组号));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "合体序号"), Py_BuildValue("i", 机体列表[r_idx].合体序号));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "分离机体"), Py_BuildValue("i", 机体列表[r_idx].分离机体));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "合体数"), Py_BuildValue("i", 机体列表[r_idx].合体数));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "换装系统"), Py_BuildValue("i", 机体列表[r_idx].换装系统));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "机体BGM"), Py_BuildValue("i", 机体列表[r_idx].机体BGM));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "空适应"), Py_BuildValue("i", 机体列表[r_idx].空适应));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "陆适应"), Py_BuildValue("i", 机体列表[r_idx].陆适应));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "海适应"), Py_BuildValue("i", 机体列表[r_idx].海适应));
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "宇适应"), Py_BuildValue("i", 机体列表[r_idx].宇适应));

        PyObject *WeaponList = PyList_New(0);
        for (UINT8 w_idx = 0; w_idx < w_count; w_idx++)
        {
            PyObject *WeaponDict = PyDict_New();

            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "代码"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].代码));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "新人类"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].新人类));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "圣战士"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].圣战士));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "气力"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].气力));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "改造类型"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].改造类型));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "近射程"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].近射程));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "远射程"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].远射程));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "地图武器分类"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].地图武器分类));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "着弹点指定型攻击半径"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].着弹点指定型攻击半径));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "攻击力"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].攻击力));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "分类"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].分类));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "属性"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].属性));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "改造追加"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].改造追加));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "武器"), decode(机体列表[r_idx].武器列表[w_idx].武器, ExtraDict, TransDict));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "方向指定型范围"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].方向指定型范围));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "地图武器演出"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].地图武器演出));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "ＥＮ"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].ＥＮ));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "命中"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].命中));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "ＣＴ"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].ＣＴ));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "初期弹数"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].初期弹数));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "最大弹数"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].最大弹数));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "空适应"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].空适应));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "陆适应"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].陆适应));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "海适应"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].海适应));
            PyDict_SetItem(WeaponDict, Py_BuildValue("s", "宇适应"), Py_BuildValue("i", 机体列表[r_idx].武器列表[w_idx].宇适应));

            PyList_Append(WeaponList, WeaponDict);
        }
        PyDict_SetItem(RobotDict, Py_BuildValue("s", "武器列表"), WeaponList);

        PyList_Append(RobotList, RobotDict);
    }

    PyObject *DataDict = PyDict_New();
    PyDict_SetItem(DataDict, Py_BuildValue("s", "机体列表"), RobotList);

    return DataDict;
}

static PyObject *ROBOT_build(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *DataDict, *ExtraDict, *TransDict;
    char *kw_list[] = {"buffer", "extra", "trans", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OOO", kw_list, &DataDict, &ExtraDict, &TransDict))
        return NULL;

    PyObject *RobotList = PyDict_GetItem(DataDict, Py_BuildValue("s", "机体列表"));
    UINT16 r_count = (UINT16)PyList_Size(RobotList);
    UINT8 w_count = 0x10;
    ROBOT *机体列表 = (ROBOT *)calloc(r_count, sizeof(ROBOT));

    for (UINT16 r_idx = 0; r_idx < r_count; r_idx++)
    {
        PyObject *RobotDict = PyList_GetItem(RobotList, r_idx);

        strcpy(机体列表[r_idx].机体, encode(PyDict_GetItem(RobotDict, Py_BuildValue("s", "机体")), ExtraDict, TransDict));
        机体列表[r_idx].代码 = (UINT16)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "代码")));
        机体列表[r_idx].移动类型 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "移动类型")));
        机体列表[r_idx].移动力 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "移动力")));
        机体列表[r_idx].ＨＰ = (UINT16)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "ＨＰ")));
        机体列表[r_idx].ＥＮ = (UINT16)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "ＥＮ")));
        机体列表[r_idx].运动性 = (UINT16)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "运动性")));
        机体列表[r_idx].装甲 = (UINT16)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "装甲")));
        机体列表[r_idx].限界 = (UINT16)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "限界")));
        机体列表[r_idx].体积 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "体积")));
        机体列表[r_idx].芯片 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "芯片")));
        机体列表[r_idx].换乘系 = (UINT16)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "换乘系")));
        机体列表[r_idx].特性 = (UINT32)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "特性")));
        机体列表[r_idx].修理费 = (UINT16)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "修理费")));
        机体列表[r_idx].资金 = (UINT16)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "资金")));
        机体列表[r_idx].变形组号 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "变形组号")));
        机体列表[r_idx].变形序号 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "变形序号")));
        机体列表[r_idx].合体组号 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "合体组号")));
        机体列表[r_idx].合体序号 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "合体序号")));
        机体列表[r_idx].分离机体 = (UINT16)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "分离机体")));
        机体列表[r_idx].合体数 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "合体数")));
        机体列表[r_idx].换装系统 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "换装系统")));
        机体列表[r_idx].机体BGM = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "机体BGM")));
        机体列表[r_idx].空适应 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "空适应")));
        机体列表[r_idx].陆适应 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "陆适应")));
        机体列表[r_idx].海适应 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "海适应")));
        机体列表[r_idx].宇适应 = (UINT8)PyLong_AsLong(PyDict_GetItem(RobotDict, Py_BuildValue("s", "宇适应")));

        PyObject *WeaponList = PyDict_GetItem(RobotDict, Py_BuildValue("s", "武器列表"));
        for (UINT8 w_idx = 0; w_idx < w_count; w_idx++)
        {
            PyObject *WeaponDict = PyList_GetItem(WeaponList, w_idx);
            机体列表[r_idx].武器列表[w_idx].代码 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "代码")));
            机体列表[r_idx].武器列表[w_idx].新人类 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "新人类")));
            机体列表[r_idx].武器列表[w_idx].圣战士 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "圣战士")));
            机体列表[r_idx].武器列表[w_idx].气力 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "气力")));
            机体列表[r_idx].武器列表[w_idx].改造类型 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "改造类型")));
            机体列表[r_idx].武器列表[w_idx].近射程 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "近射程")));
            机体列表[r_idx].武器列表[w_idx].远射程 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "远射程")));
            机体列表[r_idx].武器列表[w_idx].地图武器分类 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "地图武器分类")));
            机体列表[r_idx].武器列表[w_idx].着弹点指定型攻击半径 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "着弹点指定型攻击半径")));
            机体列表[r_idx].武器列表[w_idx].攻击力 = (UINT16)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "攻击力")));
            机体列表[r_idx].武器列表[w_idx].分类 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "分类")));
            机体列表[r_idx].武器列表[w_idx].属性 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "属性")));
            机体列表[r_idx].武器列表[w_idx].改造追加 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "改造追加")));
            strcpy(机体列表[r_idx].武器列表[w_idx].武器, encode(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "武器")), ExtraDict, TransDict));
            机体列表[r_idx].武器列表[w_idx].方向指定型范围 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "方向指定型范围")));
            机体列表[r_idx].武器列表[w_idx].地图武器演出 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "地图武器演出")));
            机体列表[r_idx].武器列表[w_idx].ＥＮ = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "ＥＮ")));
            机体列表[r_idx].武器列表[w_idx].命中 = (INT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "命中")));
            机体列表[r_idx].武器列表[w_idx].ＣＴ = (INT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "ＣＴ")));
            机体列表[r_idx].武器列表[w_idx].初期弹数 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "初期弹数")));
            机体列表[r_idx].武器列表[w_idx].最大弹数 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "最大弹数")));
            机体列表[r_idx].武器列表[w_idx].空适应 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "空适应")));
            机体列表[r_idx].武器列表[w_idx].陆适应 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "陆适应")));
            机体列表[r_idx].武器列表[w_idx].海适应 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "海适应")));
            机体列表[r_idx].武器列表[w_idx].宇适应 = (UINT8)PyLong_AsLong(PyDict_GetItem(WeaponDict, Py_BuildValue("s", "宇适应")));
        }
    }
    PyObject *BufByte = PyByteArray_FromStringAndSize((char *)机体列表, sizeof(ROBOT) * r_count);
    free(机体列表);

    return BufByte;
}

const char parse_doc[] = "parse(buf: bytearray, extra: dict, trans: dict) -> dict";
const char build_doc[] = "build(data: dict, extra: dict, trans: dict) -> bytearray";

static PyMethodDef ROBOTMethods[] =
    {
        {"parse", (PyCFunction)ROBOT_parse, METH_VARARGS | METH_KEYWORDS, parse_doc},
        {"build", (PyCFunction)ROBOT_build, METH_VARARGS | METH_KEYWORDS, build_doc},
        {NULL, NULL, 0, NULL}};

static struct PyModuleDef ROBOT_module =
    {
        PyModuleDef_HEAD_INIT,
        "ROBOT",
        "ROBOT.raf Parser",
        -1,
        ROBOTMethods};

PyMODINIT_FUNC PyInit_ROBOT(void)
{
    PyObject *module;
    module = PyModule_Create(&ROBOT_module);
    if (module == NULL)
        return NULL;
    return module;
}
