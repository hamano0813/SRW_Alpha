"""
核心数据解析包

管理所有 ROM 二进制文件的 C 扩展解析器和 ROM 数据中枢。
子模块按文件类型拆分，各 s 扩展通过对称的 parse/build 接口对外暴露。

Modules:
    rom: ROM 数据中枢，管理缓存加载/保存
    lzss: LZSS 压缩算法
    codec: Shift-JIS X0213 编解码器
    robot_raf: ROBOT.RAF 解析/构建
    snmsg_bin: SNMSG.BIN 解析/构建
    sndata_bin: SNDATA.BIN 解析/构建
    dc_bin: DC.BIN 解析/构建
    dr_bin: DR.BIN 解析/构建
    pilot_bin: PILOT.BIN 解析/构建
"""
