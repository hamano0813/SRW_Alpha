/*
 * sndata.c -- SNDATA.BIN parser/builder C extension
 *
 * SNDATA.BIN stores scenario command data in a flat binary:
 *   [0x0000]  UINT32 场景指针[0x200]  —— 指向各 SCENARIO 的绝对偏移
 *   [0x0800]  SCENARIO[0x8C]          —— 连续排列，每块 0x4048 字节
 *
 * 每块 SCENARIO (0x4048 字节)：
 *   [0x00]  UINT32 区块数量（固定 0x10）
 *   [0x04]  UINT32 指针宽度（固定 0x04）
 *   [0x08]  UINT32 区块指针[0x10]    → 指向 0x48 起的指令流偏移（单位=2B）
 *   [0x48]  指令流 …                 → 连续指令直到 0xFF 终止
 *   [余下]  0xFF 填充
 *
 * 指令格式：<code(1B) count(1B)> param[...]  总长 = count × 2
 * count=1 → 无参数；count≥2 → (count-1) 个 INT16 参数
 * code=0x00 → BLOCK 申明，param[0] = 区块编号（0~0x0A）
 * 区块指针[0] 固定为 0（指向 BLOCK(0) 的起始）
 * 区块指针[1~0x0A] 指向各 BLOCK 申明指令（单位偏移）
 * 区块指针[0x0B~0x0F] 未使用 → 0xFFFFFFFF
 *
 * Python API (via _sndata.pyd):
 *   parse(data: bytearray | bytes, extra=None) -> dict
 *   build(data: dict, extra=None) -> bytearray
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ===================================================================
 * 常量
 * =================================================================== */

#define SP_QTY           0x200   /* 场景指针表条目数 */
#define SCENARIO_COUNT   0x8C    /* 有效场景数 */
#define SCENARIO_SIZE    0x4048  /* 每场景定长 */
#define BLOCK_QTY        0x10    /* 区块指针数 */
#define CMD_DATA_SIZE    0x4000  /* 指令区最大字节 */
#define HEADER_SIZE      0x48    /* 场景头部字节数 */

/* ===================================================================
 * Little-endian 读写
 * =================================================================== */

static uint32_t r32(const unsigned char *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8)
         | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void w32(unsigned char *p, uint32_t v)
{
    p[0] = (unsigned char)(v & 0xFF);
    p[1] = (unsigned char)((v >> 8) & 0xFF);
    p[2] = (unsigned char)((v >> 16) & 0xFF);
    p[3] = (unsigned char)((v >> 24) & 0xFF);
}

static int16_t r16_s(const unsigned char *p)
{
    return (int16_t)(p[0] | ((uint32_t)p[1] << 8));
}

static void w16(unsigned char *p, int16_t v)
{
    p[0] = (unsigned char)((uint16_t)v & 0xFF);
    p[1] = (unsigned char)(((uint16_t)v >> 8) & 0xFF);
}

/* ===================================================================
 * 辅助：解析单场景指令流
 *
 * 从 data[off] 开始读取连续指令，直到 0xFF 终止或超限。
 * 返回 Python list，每个元素为 {"code": int, "count": int, "params": [int, ...]}。
 * =================================================================== */

static PyObject *
parse_commands(const unsigned char *data, Py_ssize_t off, Py_ssize_t max_off)
{
    PyObject *cmd_list = PyList_New(0);
    if (!cmd_list)
        return NULL;

    while (off < max_off)
    {
        unsigned char code = data[off];
        if (code == 0xFF)
            break;

        unsigned char cnt = data[off + 1];
        Py_ssize_t length = (Py_ssize_t)cnt * 2;

        if (length < 2 || off + length > max_off)
            break;

        PyObject *cmd_dict = PyDict_New();
        if (!cmd_dict)
        {
            Py_DECREF(cmd_list);
            return NULL;
        }

        PyDict_SetItemString(cmd_dict, "code", PyLong_FromLong(code));
        PyDict_SetItemString(cmd_dict, "count", PyLong_FromLong(cnt));

        PyObject *param_list = PyList_New(0);
        if (!param_list)
        {
            Py_DECREF(cmd_dict);
            Py_DECREF(cmd_list);
            return NULL;
        }

        for (int i = 0; i < (int)(cnt - 1); i++)
        {
            int16_t val = r16_s(data + off + 2 + (size_t)i * 2);
            PyList_Append(param_list, PyLong_FromLong((long)val));
        }

        PyDict_SetItemString(cmd_dict, "params", param_list);
        PyDict_SetItemString(cmd_dict, "explain", PyUnicode_FromString(""));
        Py_DECREF(param_list);

        PyList_Append(cmd_list, cmd_dict);
        Py_DECREF(cmd_dict);

        off += length;
    }

    return cmd_list;
}

/* ===================================================================
 * Python API: parse
 *
 *   parse(data, extra=None) -> dict
 *
 * 返回:
 *   { "scenarios": [ { "block_pointers": [...], "commands": [...] }, ... ] }
 * =================================================================== */

static PyObject *
sndata_parse(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"data", "extra", NULL};
    Py_buffer view;
    PyObject *extra = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y*|O", (char **)kwlist,
                                     &view, &extra))
        return NULL;

    /* 检查文件大小 */
    Py_ssize_t file_size = view.len;
    Py_ssize_t expected_min = 0x800 + SCENARIO_SIZE;
    if (file_size < expected_min)
    {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_ValueError, "SNDATA.BIN too short");
        return NULL;
    }

    const unsigned char *raw = (const unsigned char *)view.buf;

    /* 验证指针表头 */
    uint32_t first_ptr = r32(raw);
    if (first_ptr != 0x800)
    {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_ValueError,
                        "First scenario pointer is not 0x800");
        return NULL;
    }

    /* 主返回字典 */
    PyObject *result = PyDict_New();
    if (!result)
    {
        PyBuffer_Release(&view);
        return NULL;
    }

    PyObject *scenarios_list = PyList_New(0);
    if (!scenarios_list)
    {
        Py_DECREF(result);
        PyBuffer_Release(&view);
        return NULL;
    }
    PyDict_SetItemString(result, "scenarios", scenarios_list);
    Py_DECREF(scenarios_list);

    PyDict_SetItemString(result, "count", PyLong_FromLong(SCENARIO_COUNT));

    for (int i = 0; i < SCENARIO_COUNT; i++)
    {
        uint32_t sc_ptr = r32(raw + (size_t)i * 4);
        if (sc_ptr == 0)
            continue;

        PyObject *sc_dict = PyDict_New();
        if (!sc_dict)
        {
            Py_DECREF(result);
            PyBuffer_Release(&view);
            return NULL;
        }

        /* 区块指针 */
        uint32_t block_ptrs[BLOCK_QTY];
        for (int j = 0; j < BLOCK_QTY; j++)
            block_ptrs[j] = r32(raw + sc_ptr + 8 + (size_t)j * 4);

        PyObject *ptr_list = PyList_New(BLOCK_QTY);
        if (!ptr_list)
        {
            Py_DECREF(sc_dict);
            Py_DECREF(result);
            PyBuffer_Release(&view);
            return NULL;
        }
        for (int j = 0; j < BLOCK_QTY; j++)
        {
            int32_t val = (int32_t)block_ptrs[j];
            PyList_SetItem(ptr_list, j, PyLong_FromLong((long)val));
        }
        PyDict_SetItemString(sc_dict, "block_pointers", ptr_list);
        Py_DECREF(ptr_list);

        /* 指令流 */
        Py_ssize_t cmd_start = (Py_ssize_t)sc_ptr + HEADER_SIZE;
        Py_ssize_t cmd_end = cmd_start + CMD_DATA_SIZE;
        if (cmd_end > file_size)
            cmd_end = file_size;

        PyObject *commands = parse_commands(raw, cmd_start, cmd_end);
        if (!commands)
        {
            Py_DECREF(sc_dict);
            Py_DECREF(result);
            PyBuffer_Release(&view);
            return NULL;
        }
        PyDict_SetItemString(sc_dict, "commands", commands);
        Py_DECREF(commands);

        PyList_Append(scenarios_list, sc_dict);
        Py_DECREF(sc_dict);
    }

    PyBuffer_Release(&view);
    return result;
}

/* ===================================================================
 * 辅助：从指令列表计算区块指针
 *
 * 遍历 commands，对每个 code=0x00 的指令（BLOCK 申明），
 * 将区块指针[param[0]] 设为当前单位偏移。
 * 未使用的区块指针置为 -1 (0xFFFFFFFF)。
 * =================================================================== */

static void
compute_block_pointers(PyObject *cmd_list, int32_t *block_ptrs)
{
    /* 初始化为 -1 */
    for (int i = 0; i < BLOCK_QTY; i++)
        block_ptrs[i] = -1;

    Py_ssize_t count = PyList_Size(cmd_list);
    Py_ssize_t unit_off = 0;  /* 当前指令在 0x48 后的单位偏移 */

    for (Py_ssize_t i = 0; i < count; i++)
    {
        PyObject *cmd = PyList_GetItem(cmd_list, i);
        if (!cmd || !PyDict_Check(cmd))
        {
            unit_off += 1;  /* 至少 1 单位，跳过 */
            continue;
        }

        int code = (int)PyLong_AsLong(PyDict_GetItemString(cmd, "code"));
        int cnt  = (int)PyLong_AsLong(PyDict_GetItemString(cmd, "count"));
        int length = cnt * 2;  /* 字节长度 */

        if (code == 0x00)
        {
            PyObject *params = PyDict_GetItemString(cmd, "params");
            if (params && PyList_Check(params) && PyList_Size(params) > 0)
            {
                long block_id = PyLong_AsLong(PyList_GetItem(params, 0));
                if (block_id >= 0 && block_id < BLOCK_QTY)
                    block_ptrs[block_id] = (int32_t)unit_off;
            }
        }

        /* 前进单位偏移（单位 = 2B） */
        unit_off += length / 2;
    }
}

/* ===================================================================
 * 辅助：写入指令流
 *
 * 将 commands 列表写入 buf，返回写入的总字节数（含 0xFF 终止）。
 * 写入位置从 offset 开始。返回 -1 表示溢出。
 * =================================================================== */

static int
write_commands(PyObject *cmd_list, unsigned char *buf,
               Py_ssize_t offset, Py_ssize_t max_size)
{
    Py_ssize_t count = PyList_Size(cmd_list);
    Py_ssize_t pos = offset;

    for (Py_ssize_t i = 0; i < count; i++)
    {
        PyObject *cmd = PyList_GetItem(cmd_list, i);
        if (!cmd || !PyDict_Check(cmd))
            continue;

        int code   = (int)PyLong_AsLong(PyDict_GetItemString(cmd, "code"));
        int cnt    = (int)PyLong_AsLong(PyDict_GetItemString(cmd, "count"));
        int length = cnt * 2;

        if (code == 0xFF)
            break;  /* 终止码在最后统一写入 */

        if (pos + length > max_size)
            return -1;

        buf[pos]     = (unsigned char)code;
        buf[pos + 1] = (unsigned char)cnt;

        PyObject *params = PyDict_GetItemString(cmd, "params");
        if (params && PyList_Check(params))
        {
            Py_ssize_t pcount = PyList_Size(params);
            if (pcount > cnt - 1)
                pcount = cnt - 1;
            for (Py_ssize_t j = 0; j < pcount; j++)
            {
                PyObject *pv = PyList_GetItem(params, j);
                long val = 0;
                if (pv && PyLong_Check(pv))
                    val = PyLong_AsLong(pv);
                w16(buf + pos + 2 + (size_t)j * 2, (int16_t)val);
            }
        }

        pos += length;
    }

    /* 0xFF 终止 */
    if (pos >= max_size)
        return -1;
    buf[pos++] = 0xFF;

    return (int)(pos - offset);
}

/* ===================================================================
 * Python API: build
 *
 *   build(data, extra=None) -> bytearray
 *
 * 从 Python dict 重建 SNDATA.BIN 二进制。
 * 区块指针由指令列表动态生成，不依赖原始数据（无缓存/作弊）。
 * 整张场景以 0xFF 为底，然后覆写头部和指令流。
 * =================================================================== */

static PyObject *
sndata_build(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"data", "extra", NULL};
    PyObject *py_dict;
    PyObject *extra = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!|O", (char **)kwlist,
                                     &PyDict_Type, &py_dict, &extra))
        return NULL;

    /* 取 scenarios 列表 */
    PyObject *scenarios = PyDict_GetItemString(py_dict, "scenarios");
    if (!scenarios || !PyList_Check(scenarios))
    {
        PyErr_SetString(PyExc_KeyError,
                        "Missing or invalid 'scenarios' list");
        return NULL;
    }

    Py_ssize_t sc_count = PyList_Size(scenarios);
    if (sc_count != SCENARIO_COUNT)
    {
        PyErr_Format(PyExc_ValueError,
                     "Expected %d scenarios, got %zd",
                     SCENARIO_COUNT, sc_count);
        return NULL;
    }

    /* 计算文件总大小 */
    size_t total_size = 0x800 + (size_t)sc_count * SCENARIO_SIZE;

    /* 整张缓存区以 0xFF 填充（场景数据底） */
    unsigned char *buf = (unsigned char *)malloc(total_size);
    if (!buf)
        return PyErr_NoMemory();
    memset(buf, 0xFF, total_size);

    /* 指针表清 0 */
    memset(buf, 0, 0x800);

    /* 写场景指针 */
    for (Py_ssize_t i = 0; i < sc_count; i++)
        w32(buf + (size_t)i * 4,
            (uint32_t)(0x800 + (size_t)i * SCENARIO_SIZE));

    /* 结束标记指针 = 文件总大小 */
    w32(buf + (size_t)SCENARIO_COUNT * 4, (uint32_t)total_size);

    /* 逐个构建场景 */
    for (Py_ssize_t i = 0; i < sc_count; i++)
    {
        PyObject *sc = PyList_GetItem(scenarios, i);
        if (!sc || !PyDict_Check(sc))
        {
            free(buf);
            PyErr_SetString(PyExc_TypeError,
                            "Each scenario must be a dict");
            return NULL;
        }

        size_t sc_offset = 0x800 + (size_t)i * SCENARIO_SIZE;
        unsigned char *sc_buf = buf + sc_offset;

        /* ----- 计算区块指针（从指令列表动态生成）----- */
        PyObject *cmd_list = PyDict_GetItemString(sc, "commands");
        if (!cmd_list || !PyList_Check(cmd_list))
        {
            free(buf);
            PyErr_SetString(PyExc_KeyError,
                            "Missing or invalid 'commands' in scenario");
            return NULL;
        }

        int32_t block_ptrs[BLOCK_QTY];
        compute_block_pointers(cmd_list, block_ptrs);

        /* ----- 写场景头部 ----- */
        w32(sc_buf, BLOCK_QTY);                          /* 区块数量 */
        w32(sc_buf + 4, 4);                              /* 指针宽度 */

        for (int j = 0; j < BLOCK_QTY; j++)
            w32(sc_buf + 8 + (size_t)j * 4,
                (uint32_t)(uint32_t)block_ptrs[j]);

        /* ----- 写指令流 ----- */
        int cmd_written = write_commands(
            cmd_list, buf,
            (Py_ssize_t)(sc_offset + HEADER_SIZE),
            (Py_ssize_t)(sc_offset + SCENARIO_SIZE));

        if (cmd_written < 0)
        {
            free(buf);
            PyErr_SetString(PyExc_ValueError,
                            "Command data exceeds scenario size");
            return NULL;
        }

        /* 指令区剩余部分保持 0xFF（已由全填充保证） */
    }

    PyObject *result = PyByteArray_FromStringAndSize(
        (char *)buf, (Py_ssize_t)total_size);
    free(buf);
    return result;
}

/* ===================================================================
 * 模块方法表
 * =================================================================== */

static PyMethodDef SndataMethods[] = {
    {"parse", (PyCFunction)sndata_parse, METH_VARARGS | METH_KEYWORDS,
     "Parse SNDATA.BIN data into a Python dict."},
    {"build", (PyCFunction)sndata_build, METH_VARARGS | METH_KEYWORDS,
     "Build SNDATA.BIN binary data from a Python dict."},
    {NULL, NULL, 0, NULL}
};

/* ===================================================================
 * 模块定义
 * =================================================================== */

static struct PyModuleDef sndata_module = {
    PyModuleDef_HEAD_INIT,
    "_sndata",
    "SNDATA.BIN parser/builder",
    -1,
    SndataMethods,
};

/* ===================================================================
 * 模块入口
 * =================================================================== */

PyMODINIT_FUNC PyInit__sndata(void)
{
    return PyModule_Create(&sndata_module);
}
