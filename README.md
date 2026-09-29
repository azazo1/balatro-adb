# balatro-adb

用 adb 在 Android 设备上操控 Balatro (小丑牌) 的 skill, 附带一份中文规则手册作为决策参考.

入口是 [SKILL.md](SKILL.md), 它说明何时使用, 环境前提, 三条最容易踩的坐标系结论, 固定五步操作循环,
以及全部参考文件的索引.

## 为什么是一个 skill

这台设备上的 Balatro 是 Love2D 打包的, 没有 view 层级, `uiautomator dump` 拿不到任何控件.
于是整条链路只有 "看截图 + 发点击" 两种手段, 需要一套明确的方法与坐标表才能稳定操作,
这类知识适合按 skill 的形式组织成可复用的流程.

## 内容

| 路径 | 内容 |
| --- | --- |
| [SKILL.md](SKILL.md) | 技能入口: 使用时机, 环境, 操作循环, 坑, 索引 |
| [references/adb/](references/adb/) | adb 操作细节: 连接, 屏幕, 输入, 读图, 布局, 循环 |
| [references/adb/pos/](references/adb/pos/README.md) | 预定义像素坐标表 (JSON + 说明), 查表即可点击 |
| [references/rules/](references/rules/) | Balatro 规则手册 (中文, 按 wiki 1.0.1o 整理) |
| [references/version-diff.md](references/version-diff.md) | 设备版本 1.0.0L 与 wiki 1.0.1o 的差异记录 |
| [scripts/adb/](scripts/adb/) | adb 辅助脚本: 截图, 连续点击, 按名字点击 |
| [scripts/](scripts/) | 抓取 wiki, 提取表格, 提取 APK 游戏数据, 校验一致性 |
| [data/](data/) | 结构化 CSV (wiki 版与小丑牌数据, 以及从 APK 提取的 1.0.0L 版) |
| [raw/](raw/) [txt/](txt/) | wiki 原始页面与纯文本 (规则手册的出处) |

## 常用命令

```shell
# 校验小丑牌表, 相对链接与坐标表的一致性
just check

# 截图 (自动重试截断, 可选缩放) 与点击
just shot /tmp/shot.png 1200
just tap 1093 946

# 查看有哪些预定义可点元素
just pos --list
```

设备用 `ADB_SERIAL` 环境变量指定; 未设置时若只有一台设备会自动选用.
脚本默认不写入 home 目录, 只使用 `/tmp`.

## 从设备重新提取游戏数据

设备上的 Balatro 可能与网上资料版本不同, 需要以设备为准时:

```shell
adb shell pm path <包名>
adb pull /data/app/~~xxx/<包名>-xxx/base.apk /tmp/base.apk
unzip -o -q /tmp/base.apk assets/game.love -d /tmp/apk
unzip -o -q /tmp/apk/assets/game.love -d /tmp/game-src
just apk-data /tmp/game-src 1.0.0L
```

## 许可

- `references/rules/`, `raw/`, `txt/`, `data/` 中的规则内容整理自 [Balatro Wiki](https://balatrowiki.org/),
  沿用其 CC BY-NC-SA 3.0 授权, 不得商用, 详见 [NOTICE.md](NOTICE.md).
- `SKILL.md`, `references/adb/`, `scripts/` 为本仓库自行编写.
