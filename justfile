# balatro-adb skill 的常用操作

# 运行 Python 脚本用的解释器, 需要 Pillow (读图) 与 pandas (提表); 可用环境变量 PYTHON 覆盖.
python := env_var_or_default("PYTHON", "python3")
# 目标设备 serial; 留空时脚本会自动选择唯一在线设备.
serial := env_var_or_default("ADB_SERIAL", "")

[private]
default:
    @just --list

# just shot [输出路径] [缩放长边]
# 截图 (POSIX shell). 截断会自动重试, 给了缩放尺寸则额外输出缩放版本.
shot out="/tmp/shot.png" scale="":
    #!/usr/bin/env bash
    set -eu
    export ADB_SERIAL="{{serial}}"
    if [ -n "{{scale}}" ]; then
        bash scripts/adb/shot.sh "{{out}}" {{scale}}
    else
        bash scripts/adb/shot.sh "{{out}}"
    fi

# just tap X Y [X Y ...]
# 连续点击若干坐标, 每个点之间停顿 TAP_DELAY 秒 (默认 0.4).
tap +coords:
    #!/usr/bin/env bash
    set -eu
    export ADB_SERIAL="{{serial}}"
    bash scripts/adb/tap.sh {{coords}}

# just pos [args...]
# 坐标表查询: --list 列出全部元素, 或给出元素名点击, 例如 just pos mainGame.buttons.play.
pos +args:
    #!/usr/bin/env bash
    set -eu
    export ADB_SERIAL="{{serial}}"
    {{python}} scripts/adb/tap_at.py {{args}}

# just hand N [--indices i ...] [--tap]
# 按 N 张手牌算出各张牌的点击点; 加 --tap 直接点击.
hand +args:
    #!/usr/bin/env bash
    set -eu
    export ADB_SERIAL="{{serial}}"
    {{python}} scripts/adb/tap_at.py --hand {{args}}

# just check
# 校验小丑牌表条目, markdown 相对链接与坐标表的一致性.
check:
    {{python}} scripts/check_docs.py

# just fetch
# 重新抓取 Balatro Wiki 的规则页面到 raw/ 与 txt/ (需要 curl 与 pandoc).
fetch:
    bash scripts/fetch-pages.sh

# just tables
# 从 raw/ 重新提取表格到 data/ (需要 pandas).
tables:
    {{python}} scripts/extract_tables.py

# just apk-data SRC VERSION
# 从解包后的 game.love 源码目录提取小丑牌数据到 data/game-VERSION/.
apk-data src version:
    {{python}} scripts/extract_apk_game_data.py {{quote(src)}} --version {{version}}
