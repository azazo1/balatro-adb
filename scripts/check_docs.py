#!/usr/bin/env python3
"""校验仓库内部一致性: 手册条目, 相对链接, 坐标表.

用法: python3 scripts/check_docs.py
"""

import csv
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
RULES = ROOT / "references" / "rules"
JOKER_DOC = RULES / "04-jokers.md"
WIKI_JOKERS = ROOT / "data" / "Jokers.1.csv"
POSITIONS = ROOT / "references" / "adb" / "pos" / "positions.json"

NUM_COLUMN = re.compile(r"\|\s*(\d+)\s*\|")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+)\)")


def check_joker_table() -> None:
    """手册的小丑牌表: 编号连续且名称与 wiki 数据一致."""
    text = JOKER_DOC.read_text(encoding="utf-8")
    numbers = [int(NUM_COLUMN.match(line).group(1)) for line in text.splitlines() if NUM_COLUMN.match(line)]
    if numbers != list(range(1, 151)):
        raise SystemExit(f"小丑牌编号不连续: 共 {len(numbers)} 条")

    with WIKI_JOKERS.open() as fh:
        names = {int(row["Nr"]): row["Joker"] for row in csv.DictReader(fh)}

    missing = [n for n in range(1, 151) if f"({names[n]})" not in text]
    if missing:
        raise SystemExit(f"手册中缺少这些编号的小丑牌名称: {missing}")
    print(f"小丑牌表 {len(numbers)} 条, 编号连续, 名称与 wiki 数据一致")


def check_links() -> None:
    """所有 markdown 里的相对链接都要能落到真实文件."""
    broken = []
    checked = 0
    for md in ROOT.rglob("*.md"):
        if ".git" in md.parts:
            continue
        for target in MD_LINK.findall(md.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("mailto:"):
                continue
            checked += 1
            resolved = (md.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{md.relative_to(ROOT)} -> {target}")
    if broken:
        raise SystemExit("失效链接:\n  " + "\n  ".join(broken))
    print(f"相对链接 {checked} 个全部有效")


def check_positions() -> None:
    """坐标表: 每个元素都要有可用的 tap 点, box 与 tap 不矛盾."""
    tree = json.loads(POSITIONS.read_text(encoding="utf-8"))

    def walk(node: dict, prefix: str = "") -> list[tuple[str, dict]]:
        out = []
        for key, value in node.items():
            if key == "meta":
                continue
            name = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                if "tap" in value:
                    out.append((name, value))
                out.extend(walk(value, name))
        return out

    nodes = walk(tree)
    if not nodes:
        raise SystemExit("坐标表里没有任何可点元素")

    problems = []
    for name, node in nodes:
        x, y = node["tap"]
        box = node.get("box")
        if box:
            x0, y0, x1, y1 = box
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                problems.append(f"{name}: tap ({x}, {y}) 不在 box {box} 内")
        if not (0 <= x < 2400 and 0 <= y < 1080):
            problems.append(f"{name}: tap ({x}, {y}) 超出横屏 2400x1080 范围")
    if problems:
        raise SystemExit("坐标表问题:\n  " + "\n  ".join(problems))
    print(f"坐标表 {len(nodes)} 个元素, tap 点均在 box 内且在屏幕范围内")


def main() -> None:
    check_joker_table()
    check_links()
    check_positions()


if __name__ == "__main__":
    main()
