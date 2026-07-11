#ifndef LZSS_H
#define LZSS_H

/*
 * LZSS compression / decompression
 *
 * raw_data : uncompressed data
 * comp_data: compressed data
 */

#include <stdint.h>

#ifdef __cplusplus
extern "C"
{
#endif

    /*
     * Compress raw data to LZSS format.
     *
     * comp_data : output compressed data (allocated inside, caller must free())
     * comp_size : output compressed size
     * pack      : alignment padding (1 = no padding, 2/4/8 = align to boundary)
     *
     * return:
     *   0  success
     *   <0 error
     */
    int lzss_compress(
        const uint8_t *raw_data,
        uint32_t raw_size,

        uint8_t **comp_data,
        uint32_t *comp_size,

        uint32_t pack);

    /*
     * Decompress LZSS data to raw format.
     *
     * comp_size : size of compressed input data
     * raw_data  : output raw data (allocated inside, caller must free())
     * raw_size  : output decompressed size
     *
     * return:
     *   0  success
     *   <0 error
     */
    int lzss_decompress(
        const uint8_t *comp_data,
        uint32_t comp_size,

        uint8_t **raw_data,
        uint32_t *raw_size);

#ifdef __cplusplus
}
#endif

#endif /* LZSS_H */