#ifndef CODEC_H
#define CODEC_H

/*
 * codec.h — Codec C 内部 API 头文件
 *
 * 声明 codec_decode() / codec_encode() 供其他 C 扩展模块使用。
 *
 * 用法：
 *   在 .c 文件中 #include "../codec/codec.h"
 *   在 setup.py 中将 codec.c 添加为源文件并定义 CODEC_AS_SUBMODULE：
 *
 *   Extension("_robot_raf",
 *       sources=["robot_raf.c", "../codec/codec.c"],
 *       define_macros=[("CODEC_AS_SUBMODULE", None)])
 */

#include <Python.h>
#include <stddef.h>

/*
 * 将 Shift-JIS x0213 字节解码为 Python str。
 *
 * 处理顺序：读取到 0x00 截断 → shift_jisx0213 解码 → extra → trans。
 *
 * Parameters:
 *   s     — 字节数据指针
 *   len   — 缓冲区大小上限
 *   extra — dict[str,str] 或 NULL（游戏内码 → 显示文本）
 *   trans — dict[str,str] 或 NULL（用户自定义替换）
 *
 * Returns: new reference to Python str, or NULL on error.
 */
PyObject *codec_decode(const char *s, size_t len,
                       PyObject *extra, PyObject *trans);

/*
 * 将 Python str 编码为 Shift-JIS x0213 字节。
 *
 * 处理顺序：trans_rev → extra_rev → shift_jisx0213 编码。
 *
 * Parameters:
 *   text  — Python str
 *   extra — dict[str,str] 或 NULL
 *   trans — dict[str,str] 或 NULL
 *
 * Returns: new reference to Python bytes（不含 0x00 终结符），
 *          或 NULL on error。
 */
PyObject *codec_encode(PyObject *text, PyObject *extra, PyObject *trans);

#endif /* CODEC_H */
