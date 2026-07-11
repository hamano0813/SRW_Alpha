# PSX ISO Dump / Build 工具说明

本目录包含用于 PlayStation（PS1）CD 镜像提取与重建的工具：

* `dumpsxiso`
  用于提取 PS1 ISO 镜像内容，并生成 `mkpsxiso` 使用的 XML 项目文件。

* `mkpsxiso`
  用于根据 XML 项目文件重新构建 PS1 ISO 镜像。

项目地址：

https://github.com/Lameguy64/mkpsxiso

---

# 路径限制

当前 Windows 版本工具对文件路径字符集支持有限。

以下路径建议使用 **ASCII 字符**：

* 输入镜像路径（BIN/CUE）
* XML 文件路径
* 输出镜像路径（BIN/CUE）

推荐：

```text
D:\psx\game.cue
D:\psx\cache\
D:\psx\output\game.bin
```

不推荐：

```text
D:\游戏\game.cue
D:\修改版\output\
```

工具程序本身所在目录不受影响，可以放在中文目录中。

例如：

```text
D:\工具\PSX\dumpsxiso.exe
```

也可以正常运行。

---

# dumpsxiso

## 基本用法

```cmd
dumpsxiso [options] <input>
```

示例：

```cmd
dumpsxiso game.cue
```

或：

```cmd
dumpsxiso game.bin
```

默认会在当前工作目录生成：

```text
game\
    游戏文件...

game.xml
```

---

## 指定提取目录

使用：

```cmd
-x <path>
```

示例：

```cmd
dumpsxiso -x cache game.bin
```

生成：

```text
cache\
    游戏文件...

cache.xml
```

---

## 指定 XML 文件名

使用：

```cmd
-s <file>
```

示例：

```cmd
dumpsxiso ^
-x cache ^
-s project.xml ^
game.bin
```

生成：

```text
cache\
    游戏文件...

project.xml
```

---

## 推荐提取方式

工具链中建议固定使用工作目录：

```cmd
tools\dumpsxiso ^
-x cache ^
-s cache.xml ^
game.bin
```

结果：

```text
cache\
    游戏资源文件

cache.xml
```

---

# mkpsxiso

## 基本构建

```cmd
mkpsxiso project.xml
```

输出文件名由 XML 文件中的配置决定。

---

## 指定输出 BIN

使用：

```cmd
-o <file>
```

示例：

```cmd
mkpsxiso ^
-o output\game.bin ^
project.xml
```

---

## 指定输出 CUE

使用：

```cmd
-c <file>
```

示例：

```cmd
mkpsxiso ^
-o output\game.bin ^
-c output\game.cue ^
project.xml
```

生成：

```text
output\
    game.bin
    game.cue
```

---

# 推荐修改流程

## 1. 提取原始镜像

```cmd
dumpsxiso ^
-x cache ^
-s cache.xml ^
game.bin
```

得到：

```text
cache\
cache.xml
```

---

## 2. 修改游戏资源

直接修改 `cache` 目录中的文件。

例如：

```text
cache\
    UNITPRAM\
        PILOT.BIN
        ROBOT.RAF
```

---

## 3. 重建镜像

```cmd
mkpsxiso ^
-o output\modified.bin ^
-c output\modified.cue ^
cache.xml
```

生成：

```text
output\
    modified.bin
    modified.cue
```
