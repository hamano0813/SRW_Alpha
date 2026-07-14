"""
LZSS 压缩/解压综合测试

测试所有使用 LZSS 压缩的游戏数据文件：
  - ROBOT.RAF  (头部格式：块数量 + N 个相对偏移指针)
  - BACK.BIN   (头部格式：指针表字节数 + N 个绝对偏移指针)
  - CHARA.BIN  (同 BACK.BIN)
  - MAP.BIN    (同 BACK.BIN)

测试内容：
  1. 逐块解压所有 LZSS 块
  2. 逐块重压缩 → 再解压，对比一致性
  3. 将所有块重新组建成完整文件，再重新解析解压，做整链对比
"""

import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.lzss import compress, decompress

RES_BIN = os.path.join(os.path.dirname(__file__), "..", "res", "bin")

# ── 文件格式定义 ──────────────────────────────────────────────────

# "raf"  = ROBOT.RAF：count=块数，指针相对数据区偏移
# "bin"  = .BIN文件  ：count=指针表字节数，指针为文件绝对偏移

_FILE_SPECS = {
    "ROBOT.RAF": {
        "path": os.path.join(RES_BIN, "ROBOT.RAF"),
        "fmt": "raf",
        "expect_blocks": 486,
    },
    "BACK.BIN": {
        "path": os.path.join(RES_BIN, "BACK.BIN"),
        "fmt": "bin",
        "expect_blocks": 60,
    },
    "CHARA.BIN": {
        "path": os.path.join(RES_BIN, "CHARA.BIN"),
        "fmt": "bin",
        "expect_blocks": 409,
    },
    "MAP.BIN": {
        "path": os.path.join(RES_BIN, "MAP.BIN"),
        "fmt": "bin",
        "expect_blocks": 9,
    },
}


# ── 解析 ──────────────────────────────────────────────────────────


def parse_blocks(data: bytes, fmt: str) -> list[bytes]:
    """
    从文件数据中提取所有 LZSS 压缩块。

    Args:
        data: 完整文件内容
        fmt: "raf" 或 "bin"

    Returns:
        LZSS 压缩数据块列表
    """
    count = struct.unpack_from("<I", data, 0)[0]

    if fmt == "raf":
        block_count = count
        pointers = [struct.unpack_from("<I", data, 4 + i * 4)[0] for i in range(block_count)]
        data_start = 4 + block_count * 4
        return [
            data[data_start + pointers[i] : data_start + pointers[i + 1]] if i + 1 < block_count else data[data_start + pointers[i] :]
            for i in range(block_count)
        ]
    else:
        ptr_table_size = count
        num_pointers = ptr_table_size // 4
        num_blocks = num_pointers - 2  # 最后两个：文件大小哨兵 + 未初始化垃圾
        pointers = [struct.unpack_from("<I", data, 4 + i * 4)[0] for i in range(num_pointers)]
        return [data[pointers[i] : pointers[i + 1]] for i in range(num_blocks)]


def rebuild_file(blocks: list[bytes], fmt: str) -> bytes:
    """
    将压缩块列表重新组装为完整的文件数据（头部 + 数据区）。

    Args:
        blocks: LZSS 压缩数据块列表
        fmt: "raf" 或 "bin"

    Returns:
        完整文件字节
    """
    if fmt == "raf":
        # 相对偏移
        offsets = []
        cur = 0
        for b in blocks:
            offsets.append(cur)
            cur += len(b)

        header = struct.pack("<I", len(blocks))
        for off in offsets:
            header += struct.pack("<I", off)
        return header + b"".join(blocks)
    else:
        # 绝对偏移：数据区直接从头部后面开始
        num_ptrs = len(blocks) + 2
        ptr_table_size = num_ptrs * 4
        data_start = 4 + ptr_table_size

        offsets = []
        cur = data_start
        for b in blocks:
            offsets.append(cur)
            cur += len(b)
        offsets.append(cur)  # 文件大小哨兵
        offsets.append(0)  # 最后一个指针未初始化，写 0 占位

        header = struct.pack("<I", ptr_table_size)
        for off in offsets:
            header += struct.pack("<I", off)
        return header + b"".join(blocks)


# ── 测试 ──────────────────────────────────────────────────────────


def test_file(name: str, spec: dict) -> bool:
    """测试单个文件，返回是否全部通过。"""
    path = spec["path"]
    fmt = spec["fmt"]
    expect = spec["expect_blocks"]

    if not os.path.isfile(path):
        print(f"  [WARN] 文件不存在: {path}")
        return True

    fsize = os.path.getsize(path)
    print(f"  [INFO] 文件大小: {fsize} bytes (0x{fsize:X})")

    with open(path, "rb") as f:
        file_data = f.read()

    # 1. 解析
    blocks = parse_blocks(file_data, fmt)
    print(f"  [INFO] LZSS 块数: {len(blocks)}", end="")
    if len(blocks) != expect:
        print(f"  [WARN] 预期 {expect}，请注意", end="")
    print()

    # 2. 逐块往返
    print(f"  ┌─ 单块: 解压 → 重压缩 → 再解压")
    orig_chunks = []
    recomp_chunks = []
    ok = True

    for i, blk in enumerate(blocks):
        try:
            d1 = decompress(bytearray(blk))
            rc = compress(bytearray(d1), 4)
            d2 = decompress(bytearray(rc))
            assert d1 == d2, f"块 {i} 两次解压结果不同"
            orig_chunks.append(bytes(d1))
            recomp_chunks.append(bytes(rc))
        except Exception as e:
            print(f"  │  └── [ERROR] 块 {i}: {e}")
            ok = False

    if ok:
        orig_total = sum(len(c) for c in orig_chunks)
        comp_total = sum(len(c) for c in recomp_chunks)
        print(f"  │  └── [INFO] 全部 {len(blocks)} 块通过  " f"(解压 {orig_total}B → 重压缩 {comp_total}B, {comp_total/orig_total:.2%})")

    # 3. 文件级整链
    print(f"  └─ 文件: 重建 → 重新解析 → 整链对比")
    try:
        rebuilt = rebuild_file(recomp_chunks, fmt)
        blocks2 = parse_blocks(rebuilt, fmt)
        final_chunks = []
        for blk in blocks2:
            final_chunks.append(bytes(decompress(bytearray(blk))))

        orig_all = b"".join(orig_chunks)
        final_all = b"".join(final_chunks)

        if orig_all == final_all:
            print(f"     └── [INFO] PASS  ({len(orig_all)} bytes identical)")
        else:
            print(f"     └── [ERROR] 数据不一致: " f"原始{len(orig_all)}B vs 重建{len(final_all)}B")
            ok = False
    except Exception as e:
        print(f"     └── [ERROR] 文件级测试异常: {e}")
        ok = False

    return ok


def main():
    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║              SRW Alpha - LZSS 综合测试               ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print()

    all_ok = True
    for name, spec in _FILE_SPECS.items():
        print(f"── {name} ──────────────────────────────")
        if not test_file(name, spec):
            all_ok = False
        print()

    print("════════════════════════════════════════════════════════")
    print(f"  [INFO] {'ALL TESTS PASSED' if all_ok else 'SOME TESTS FAILED'}")
    print("════════════════════════════════════════════════════════")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
