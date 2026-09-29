#!/usr/bin/env python3
"""校验手册与小丑牌数据的一致性: 条目数量, 编号连续性, 名称匹配.

用法: python3 scripts/check_docs.py
"""

import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "docs/04-jokers.md"
SOURCE = ROOT / "data/Jokers.1.csv"

NUM_COLUMN = re.compile(r"\|\s*(\d+)\s*\|")


def main() -> None:
    text = DOC.read_text()
    numbers = [int(NUM_COLUMN.match(line).group(1)) for line in text.splitlines() if NUM_COLUMN.match(line)]
    if numbers != list(range(1, 151)):
        raise SystemExit(f"小丑牌编号不连续: 共 {len(numbers)} 条")

    with SOURCE.open() as fh:
        names = {int(row["Nr"]): row["Joker"] for row in csv.DictReader(fh)}

    missing = [n for n in range(1, 151) if f"({names[n]})" not in text]
    if missing:
        raise SystemExit(f"手册中缺少这些编号的小丑牌名称: {missing}")

    print(f"小丑牌 {len(numbers)} 条, 编号连续, 名称与 wiki 数据一致")


if __name__ == "__main__":
    main()
