#!/usr/bin/env python3
"""按名字点击预定义坐标, 或算出手牌点击点.

坐标来自 references/adb/pos/positions.json, 不需要每次算图.

用法:
    # 列出所有可点的名字
    python3 scripts/adb/tap_at.py --list

    # 点击某个元素
    python3 scripts/adb/tap_at.py mainGame.buttons.play
    python3 scripts/adb/tap_at.py shop.itemSlot2 shop.confirmBuyForSlot2 --delay 1.5

    # 算出手牌点击点 (不点击, 只打印), 并可加上点第几张
    python3 scripts/adb/tap_at.py --hand 8
    python3 scripts/adb/tap_at.py --hand 8 --indices 3 4 --tap

    # 只预览坐标, 不发点击
    python3 scripts/adb/tap_at.py mainGame.buttons.discard --dry-run

设备通过 ADB_SERIAL 环境变量指定; 未设置时, 若只有一台设备则自动使用.
"""

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
POSITIONS = ROOT / "references" / "adb" / "pos" / "positions.json"


def load_tree(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def walk(tree: dict, prefix: str = "") -> dict[str, dict]:
    """展平成 a.b.c -> 字典, 只保留带 tap 的节点."""
    out: dict[str, dict] = {}
    for key, value in tree.items():
        if key == "meta":
            continue
        name = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            if isinstance(value.get("tap"), list):
                out[name] = value
            out.update(walk(value, name))
    return out


def flat_box(node: dict) -> list[int] | None:
    box = node.get("box")
    if isinstance(box, list) and len(box) == 4:
        return box
    return None


def hand_slots(count: int, center_x: float = 1220.0, tap_y: int = 690) -> list[tuple[int, int]]:
    """手牌数量为 count 时, 每张牌的点击点."""
    spacing = 130.0 if count >= 5 else 137.0
    return [
        (int(center_x + (i - (count + 1) / 2) * spacing), tap_y) for i in range(1, count + 1)
    ]


def resolve_serial() -> str:
    serial = os.environ.get("ADB_SERIAL")
    if serial:
        return serial
    out = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True).stdout
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return parts[0]
    sys.exit("没有可用设备: 检查 adb devices 是否有状态为 device 的设备")


def tap(serial: str, x: int, y: int) -> None:
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="positions.json 里的点路径, 如 mainGame.buttons.play")
    ap.add_argument("--list", action="store_true", help="列出所有可点名字与坐标")
    ap.add_argument("--hand", type=int, metavar="N", help="按 N 张手牌算点击点")
    ap.add_argument("--indices", type=int, nargs="*", default=None, help="配合 --hand, 只取第几张 (1-based)")
    ap.add_argument("--tap", action="store_true", help="配合 --hand/--indices 真的发点击 (默认只打印)")
    ap.add_argument("--dry-run", action="store_true", help="所有元素只打印坐标, 不发点击")
    ap.add_argument("--delay", type=float, default=0.4, help="点击之间的停顿秒数 (默认 0.4)")
    args = ap.parse_args()

    if not POSITIONS.exists():
        sys.exit(f"找不到坐标表: {POSITIONS}")
    nodes = walk(load_tree(POSITIONS))

    if args.list:
        width = max(len(n) for n in nodes)
        for name, node in sorted(nodes.items()):
            box = flat_box(node)
            print(f"{name:<{width}}  tap={node['tap']}  box={box}  verified={node.get('verified', False)}")
        print(f"\n共 {len(nodes)} 个可点元素")
        print("手牌区用 --hand N 计算, 例如: --hand 8")
        return

    if args.hand is not None:
        slots = hand_slots(args.hand)
        chosen = slots if args.indices is None else [slots[i - 1] for i in args.indices if 1 <= i <= args.hand]
        for i, (x, y) in enumerate(chosen, 1):
            print(f"手牌点 ({x}, {y})")
        if args.tap and chosen:
            serial = resolve_serial()
            for x, y in chosen:
                tap(serial, x, y)
                time.sleep(args.delay)
            print(f"已点击 {len(chosen)} 张")
        return

    if not args.names:
        ap.error("需要给出元素名, 或者用 --list / --hand")

    unknown = [n for n in args.names if n not in nodes]
    if unknown:
        sys.exit(f"未知元素: {unknown}\n用 --list 查看可用名字")

    serial = None if args.dry_run else resolve_serial()
    for name in args.names:
        node = nodes[name]
        x, y = node["tap"]
        print(f"{name} -> ({x}, {y})")
        if serial:
            tap(serial, x, y)
            time.sleep(args.delay)
    if not serial:
        print("dry-run, 未发送点击")


if __name__ == "__main__":
    main()
