/*
 * lzss.c
 *
 * LZSS compression / decompression
 *
 * Format:
 *   +----------------+
 *   | raw_size 4byte |
 *   +----------------+
 *   | reserved 4byte |
 *   +----------------+
 *   | LZSS stream    |
 *   +----------------+
 *
 */

#include "lzss.h"
#include <stdlib.h>
#include <string.h>
#include <limits.h>

/*
 * LZSS parameters
 *
 * window size : 4096 bytes
 * position    : 12 bits
 * length      : 4 bits
 *
 * match length:
 *   stored : 0 ~ 15
 *   actual : 3 ~ 18
 *
 */
#define THRESHOLD 2

#define PBIT 4
#define WBIT 12

#define PSIZE (1 << PBIT) // 16
#define WSIZE (1 << WBIT) // 4096

/*
 * Initial zero padding size.
 *
 * The original implementation uses a zero-filled
 * prefix before real data to simulate the initial
 * sliding window state.
 */
#define BSIZE (WSIZE - PSIZE - THRESHOLD)

#define HEAD 8 // raw_size + reserved

#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))

/*
 * Read little-endian uint32
 */
static uint32_t read_size(const uint8_t *buf)
{
    return ((uint32_t)buf[0]) |
           ((uint32_t)buf[1] << 8) |
           ((uint32_t)buf[2] << 16) |
           ((uint32_t)buf[3] << 24);
}

/*
 * Write little-endian uint32
 */
static void write_size(uint8_t *buf, uint32_t size)
{
    buf[0] = size & 0xff;
    buf[1] = (size >> 8) & 0xff;
    buf[2] = (size >> 16) & 0xff;
    buf[3] = (size >> 24) & 0xff;
}

/*
 * Adjust search start position.
 *
 * The initial window is filled with zeros.
 * Avoid matching against zero padding when
 * real data contains non-zero bytes.
 */
static int adjust_search_start(const uint8_t *buf, int r_cur, int cur, int cnt)
{
    for (int i = 0; i < cnt; i++)
    {
        if (buf[r_cur + i] != 0)
            return MAX(BSIZE - i, cur);
    }

    return cur;
}

/*
 * Search matching string in sliding window.
 *
 * Return:
 *   position of match
 *   -1 if not found
 */
static int find_match(const uint8_t *buf, int r_cur, int cur, int cnt)
{
    cur = adjust_search_start(buf, r_cur, cur, cnt);

    for (; cur < r_cur; cur++)
    {
        int i;

        for (i = 0; i < cnt; i++)
        {
            if (buf[cur + i] != buf[r_cur + i])
                break;
        }

        if (i == cnt)
            return cur;
    }

    return -1;
}

/*
 * Compress raw data to LZSS format.
 */
int lzss_compress(
    const uint8_t *raw_data,
    uint32_t raw_size,
    uint8_t **comp_data,
    uint32_t *comp_size,
    uint32_t pack)
{
    /*
     * Worst case:
     *
     * header
     * + every 8 bytes need one flag byte
     * + raw data
     */
    uint32_t max_size = HEAD + raw_size + raw_size / CHAR_BIT + 1;

    if (pack > 1 && max_size % pack)
        max_size += pack - max_size % pack;

    uint8_t *input = calloc(BSIZE + raw_size, 1);
    if (input == NULL)
        return -1;

    /* Copy raw data after zero prefix. */
    memcpy(input + BSIZE, raw_data, raw_size);

    uint8_t *output = calloc(max_size, 1);
    if (output == NULL)
    {
        free(input);
        return -1;
    }

    /* Store original size. */
    write_size(output, raw_size);

    /* reserved 4 bytes remain zero. */

    int input_size = BSIZE + raw_size;

    int r_cur = BSIZE;
    int w_cur = HEAD;

    int flag_pos = 0;
    int flag_bit = CHAR_BIT;

    while (r_cur < input_size)
    {
        /* Allocate flag byte. */
        if (flag_bit == CHAR_BIT)
        {
            flag_pos = w_cur++;
            flag_bit = 0;
        }

        int match_pos = -1;
        int match_len = THRESHOLD;

        /* Search window. */
        int search_start = MIN(r_cur - BSIZE,
                               (int)raw_size - PSIZE - THRESHOLD);

        /* Find longest match. */
        for (int len = PSIZE + THRESHOLD; len > THRESHOLD; len--)
        {
            if (r_cur + len <= input_size)
            {
                int pos = find_match(input, r_cur, search_start, len);
                if (pos >= 0)
                {
                    match_pos = pos;
                    match_len = len;
                    break;
                }
            }
        }

        if (match_len > THRESHOLD)
        {
            /*
             * Match encoding:
             *
             * byte0:
             *   position low 8 bit
             *
             * byte1:
             *   position high 4 bit
             *   length 4 bit
             */
            output[w_cur++] = match_pos & 0xff;
            output[w_cur++] = ((match_pos >> 4) & 0xf0) |
                              (match_len - THRESHOLD - 1);
            r_cur += match_len;
        }
        else
        {
            /* Literal: flag bit = 1 */
            output[w_cur++] = input[r_cur++];
            output[flag_pos] |= (1 << flag_bit);
        }

        flag_bit++;
    }

    /* Alignment padding. */
    if (pack > 1 && w_cur % pack)
        w_cur += pack - w_cur % pack;

    uint8_t *result = realloc(output, w_cur);
    if (result != NULL)
        output = result;

    free(input);

    *comp_data = output;
    *comp_size = w_cur;

    return 0;
}

/*
 * Decompress LZSS data.
 */
int lzss_decompress(
    const uint8_t *comp_data,
    uint32_t comp_size,
    uint8_t **raw_data,
    uint32_t *raw_size)
{
    if (comp_size < HEAD)
        return -1;

    uint32_t size = read_size(comp_data);

    uint8_t *output = malloc(size);
    if (output == NULL)
        return -1;

    /* Sliding window. */
    uint8_t window[WSIZE + PSIZE + THRESHOLD] = {0};

    uint32_t r_cur = HEAD;
    uint32_t w_cur = 0;

    while (r_cur < comp_size && w_cur < size)
    {
        uint8_t flags = comp_data[r_cur++];

        for (int bit = 0; bit < CHAR_BIT; bit++)
        {
            if (r_cur >= comp_size || w_cur >= size)
                break;

            if (flags & (1 << bit))
            {
                /* Literal. */
                uint8_t c = comp_data[r_cur++];
                window[w_cur & (WSIZE - 1)] = c;
                output[w_cur++] = c;
            }
            else
            {
                if (r_cur + 1 >= comp_size)
                    break;

                /* Decode match. */
                uint32_t len = (comp_data[r_cur + 1] & (PSIZE - 1)) +
                               THRESHOLD + 1;

                uint32_t pos = (((comp_data[r_cur + 1] >> PBIT) << CHAR_BIT) |
                                comp_data[r_cur]) +
                               PSIZE + THRESHOLD;

                r_cur += 2;

                for (uint32_t i = 0; i < len; i++)
                {
                    uint8_t c = window[pos & (WSIZE - 1)];
                    window[w_cur & (WSIZE - 1)] = c;
                    output[w_cur++] = c;
                    pos++;
                }
            }
        }
    }

    *raw_data = output;
    *raw_size = size;

    return 0;
}

/*
 * Python C API wrapper
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>

/*
 * Python wrapper:
 *
 * compress(raw_data, pack=1)
 *
 * raw_data:
 *      Python bytearray
 *
 * pack:
 *      output alignment
 *
 * return:
 *      compressed bytearray
 */
static PyObject *LZSS_compress(PyObject *self, PyObject *args)
{
    PyObject *in_byte;
    int pack = 1;

    if (!PyArg_ParseTuple(args, "Y|i", &in_byte, &pack))
        return NULL;

    uint8_t *raw_data = (uint8_t *)PyByteArray_AsString(in_byte);
    uint32_t raw_size = (uint32_t)PyByteArray_Size(in_byte);

    uint8_t *comp_data = NULL;
    uint32_t comp_size = 0;

    int ret = lzss_compress(raw_data, raw_size, &comp_data, &comp_size, pack);
    if (ret != 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "LZSS compression failed");
        return NULL;
    }

    PyObject *result = PyByteArray_FromStringAndSize((char *)comp_data, comp_size);
    free(comp_data);

    return result;
}

/*
 * Python wrapper:
 *
 * decompress(comp_data)
 *
 * comp_data:
 *      LZSS compressed bytearray
 *
 * return:
 *      raw bytearray
 */
static PyObject *LZSS_decompress(PyObject *self, PyObject *args)
{
    PyObject *in_byte;

    if (!PyArg_ParseTuple(args, "Y", &in_byte))
        return NULL;

    uint8_t *comp_data = (uint8_t *)PyByteArray_AsString(in_byte);
    uint32_t comp_size = (uint32_t)PyByteArray_Size(in_byte);

    uint8_t *raw_data = NULL;
    uint32_t raw_size = 0;

    int ret = lzss_decompress(comp_data, comp_size, &raw_data, &raw_size);
    if (ret != 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "LZSS decompression failed");
        return NULL;
    }

    PyObject *result = PyByteArray_FromStringAndSize((char *)raw_data, raw_size);
    free(raw_data);

    return result;
}

/*
 * Python method table
 */
static PyMethodDef LZSSMethods[] = {
    {"compress",   LZSS_compress,   METH_VARARGS,
     "Compress raw bytearray data using LZSS."},
    {"decompress", LZSS_decompress, METH_VARARGS,
     "Decompress LZSS bytearray data."},
    {NULL, NULL, 0, NULL}
};

/*
 * Module definition
 */
static struct PyModuleDef LZSS_module = {
    PyModuleDef_HEAD_INIT,
    "_lzss",
    "LZSS compression module",
    -1,
    LZSSMethods
};

/*
 * Module initialization
 */
PyMODINIT_FUNC PyInit__lzss(void)
{
    return PyModule_Create(&LZSS_module);
}
