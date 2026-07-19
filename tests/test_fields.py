"""
FieldMapping 字段映射模块测试

测试内容：
  1. 构造 FieldMapping 不抛异常
  2. 映射表中所有 key（翻译后表头）均不重复
  3. 所有 value（数据 key）均为非空字符串
  4. 各数据类型的字段数量符合预期
  5. update_mapping() 可重复调用且结果一致
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gui.custom.fields import FieldMapping

# ========== 各类型预期字段数 ==========

_EXPECTED_COUNTS: dict[str, int] = {
    "robot": 28,
    "weapon": 25,
    "pilot": 22,
    "dc": 6,
    "dr": 6,
    "skill": 10,
    "sndata": 2,
    "scenario": 4,
    "command": 4,
    "snmsg": 1,
    "script": 4,
    "aiunp": 13,
    "unknown": 50,
}


def test_construction() -> bool:
    """测试1: 构造不抛异常且映射表非空"""
    try:
        fm = FieldMapping()
    except Exception as e:
        print(f"[ERROR] 构造 FieldMapping 失败: {e}")
        return False
    if not fm._mapping:
        print("[ERROR] 映射表为空")
        return False
    print(f"[INFO] FieldMapping 构造成功，共 {len(fm._mapping)} 项")
    return True


def test_no_duplicate_keys() -> bool:
    """测试2: 映射表无重复 key"""
    fm = FieldMapping()
    seen = set()
    for k in fm._mapping:
        if k in seen:
            print(f"[ERROR] 重复 key: {k}")
            return False
        seen.add(k)
    print(f"[INFO] 全部 {len(fm._mapping)} 个 key 唯一")
    return True


def test_all_values_nonempty() -> bool:
    """测试3: 所有 value 为非空字符串"""
    fm = FieldMapping()
    for k, v in fm._mapping.items():
        if not isinstance(v, str) or not v:
            print(f"[ERROR] key={k!r} 对应的 value 为空: {v!r}")
            return False
    print(f"[INFO] 全部 value 有效")
    return True


def test_field_counts() -> bool:
    """测试4: 各数据类型字段数符合预期"""
    fm = FieldMapping()

    # 收集每个 _init_* 的字段数
    _init_methods = {
        "robot": fm._init_robot(),
        "weapon": fm._init_weapon(),
        "pilot": fm._init_pilot(),
        "dc": fm._init_dc(),
        "dr": fm._init_dr(),
        "skill": fm._init_skill(),
        "sndata": fm._init_sndata(),
        "scenario": fm._init_scenario(),
        "command": fm._init_command(),
        "snmsg": fm._init_snmsg(),
        "script": fm._init_script(),
        "aiunp": fm._init_aiunp(),
        "unknown": fm._init_unknown(),
    }

    all_ok = True
    for name, mapping in _init_methods.items():
        expected = _EXPECTED_COUNTS.get(name)
        if expected is None:
            print(f"[WARN] {name} 未配置预期字段数，跳过")
            continue
        actual = len(mapping)
        if actual != expected:
            print(f"[ERROR] {name}: 预期 {expected} 个字段，实际 {actual}")
            all_ok = False
        else:
            print(f"[INFO] {name}: {actual} 个字段")

    return all_ok


def test_update_mapping_idempotent() -> bool:
    """测试5: 重复调用 update_mapping() 结果一致"""
    fm = FieldMapping()
    snapshot1 = dict(fm._mapping)

    fm.update_mapping()
    snapshot2 = dict(fm._mapping)

    if snapshot1 != snapshot2:
        print("[ERROR] 两次 update_mapping() 结果不一致")
        return False

    # 第三次调用后仍一致
    fm.update_mapping()
    if fm._mapping != snapshot1:
        print("[ERROR] 第三次 update_mapping() 结果不一致")
        return False

    print("[INFO] update_mapping() 幂等性验证通过")
    return True


def test_common_field_keys() -> bool:
    """测试6: 常用字段 key 存在于映射表中"""
    fm = FieldMapping()
    mapping = fm._mapping

    # 这些翻译后的表头应该存在于映射中
    required_headers = [
        "code", "air", "ground", "water", "space",
        "series", "flags", "description",
    ]
    # 用 tr() 翻译后再查
    translated = {fm.tr(h) for h in required_headers}
    missing = translated - set(mapping.keys())
    if missing:
        print(f"[ERROR] 缺少常用字段: {missing}")
        return False
    print(f"[INFO] 全部常用字段存在")
    return True


def main() -> int:
    """执行所有测试并返回退出码"""
    tests = [
        ("构造测试", test_construction),
        ("key 唯一性", test_no_duplicate_keys),
        ("value 非空", test_all_values_nonempty),
        ("字段数量", test_field_counts),
        ("update_mapping 幂等性", test_update_mapping_idempotent),
        ("常用字段存在性", test_common_field_keys),
    ]

    all_ok = True
    for name, func in tests:
        ok = func()
        status = "[INFO]" if ok else "[ERROR]"
        print(f"{status} {name}: {'通过' if ok else '失败'}")
        if not ok:
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
