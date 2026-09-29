# 规则手册项目的常用操作

# 运行脚本用的 Python 解释器, 需要 pandas 等依赖; 可用环境变量 PYTHON 覆盖.
python := env_var_or_default("PYTHON", "python3")

[private]
default:
    @just --list

# just fetch
# 重新抓取 Balatro Wiki 的规则页面到 raw/ 与 txt/.
fetch:
    bash scripts/fetch-pages.sh

# just tables
# 从 raw/ 重新提取表格到 data/.
tables:
    {{python}} scripts/extract_tables.py

# just check
# 校验手册中的条目数量与编号完整性.
check:
    {{python}} scripts/check_docs.py
