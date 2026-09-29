#!/usr/bin/env python3
"""从 Balatro 安装包中提取指定版本的小丑牌数据.

数据来源是 APK 内的 Love2D 资源包:
    base.apk -> assets/game.love -> game.lua (卡牌定义) + localization/zh_CN.lua (官方中文)

用法:
    # 先解包 (无需 root, APK 通常世界可读)
    adb shell pm path <包名>
    adb pull /data/app/~~xxx/<包名>-xxx/base.apk /tmp/balatro-base.apk
    unzip -o -q /tmp/balatro-base.apk assets/game.love -d /tmp/apk
    unzip -o -q /tmp/apk/assets/game.love -d /tmp/game-src

    python3 scripts/extract_apk_game_data.py /tmp/game-src --version 1.0.0L
"""

import argparse
import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
RARITY = {"1": "Common", "2": "Uncommon", "3": "Rare", "4": "Legendary"}
HANDS_ZH = {
    "High Card": "高牌",
    "Pair": "对子",
    "Two Pair": "两对",
    "Three of a Kind": "三条",
    "Straight": "顺子",
    "Flush": "同花",
    "Full House": "葫芦",
    "Four of a Kind": "四条",
    "Straight Flush": "同花顺",
    "Royal Flush": "皇家同花顺",
    "Five of a Kind": "五条",
    "Flush House": "同花葫芦",
    "Flush Five": "同花五条",
}


def brace_block(text: str, start: int) -> str:
    """从 start 处的 `{` 开始, 返回花括号配平的整块."""
    depth, i = 0, start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
        i += 1
    return text[start:]


def entries(text: str, prefix: str = "j_") -> dict[str, str]:
    """切出所有 `前缀xxx = {...}` 条目."""
    out = {}
    for m in re.finditer(rf"\b{prefix}([a-z0-9_]+)\s*=\s*\{{", text):
        out[f"{prefix}{m.group(1)}"] = brace_block(text, m.end() - 1)
    return out


def field(body: str, name: str) -> str | None:
    m = re.search(rf"\b{name}\s*=\s*('[^']*'|\"[^\"]*\"|[-\w.]+)", body)
    return m.group(1).strip("'\"") if m else None


def config_block(body: str) -> str:
    m = re.search(r"config\s*=\s*\{", body)
    return re.sub(r"\s+", " ", brace_block(body, m.end() - 1)) if m else ""


def hand_label(text: str) -> str:
    label = HANDS_ZH.get(text, text)
    return f"{label} ({text})" if text in HANDS_ZH else text


def effect_summary(config: str) -> str:
    """把常见配置渲染成人话; 渲染不了的留空, 由 config 列兜底."""
    m = re.search(r"t_(mult|chips|xmult)\s*=\s*([\d.]+).*?type\s*=\s*'([^']+)'", config)
    if m:
        kind, value, hand = m.group(1), m.group(2), hand_label(m.group(3))
        unit = {"mult": "倍率", "chips": "筹码", "xmult": "倍率 (乘算)"}[kind]
        prefix = "X" if kind == "xmult" else "+"
        return f"{prefix}{value} {unit}, 若出牌中包含 {hand}"
    return ""


def chinese_names(loc_file: pathlib.Path) -> dict[str, str]:
    text = loc_file.read_text(encoding="utf-8")
    out = {}
    for key, body in entries(text).items():
        name = field(body, "name")
        if name:
            out[key] = name
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="解包后的 game.love 源码目录")
    ap.add_argument("--version", default="unknown", help="版本标签, 用于输出目录名")
    ap.add_argument("--locale", default="zh_CN.lua", help="本地化文件名")
    args = ap.parse_args()

    src = pathlib.Path(args.source)
    zh = chinese_names(src / "localization" / args.locale)
    version_file = src / "version.jkr"
    version = version_file.read_text(encoding="utf-8").splitlines()[0] if version_file.exists() else args.version
    print(f"游戏版本 {version}, 官方中文本地化条目 {len(zh)} 条")

    out_dir = ROOT / "data" / f"game-{args.version}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for key, body in entries((src / "game.lua").read_text(encoding="utf-8")).items():
        name_en = field(body, "name")
        if not name_en or name_en == "Locked":
            continue  # j_locked 是占位条目
        config = config_block(body)
        rows.append(
            {
                "order": field(body, "order") or "",
                "key": key,
                "name_en": name_en,
                "name_zh": zh.get(key, ""),
                "cost": field(body, "cost") or "",
                "rarity": RARITY.get(field(body, "rarity") or "", ""),
                "effect_summary": effect_summary(config),
                "config": config,
            }
        )

    rows.sort(key=lambda r: int(r["order"]) if r["order"].isdigit() else 999)
    columns = ["order", "key", "name_en", "name_zh", "cost", "rarity", "effect_summary", "config"]
    csv_path = out_dir / "jokers.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    (out_dir / "version.txt").write_text(f"{version}\n", encoding="utf-8")

    by_rarity: dict[str, int] = {}
    for r in rows:
        by_rarity[r["rarity"]] = by_rarity.get(r["rarity"], 0) + 1
    print(f"写出 {len(rows)} 张小丑牌 -> {csv_path.relative_to(ROOT)}")
    print(f"稀有度分布: {by_rarity}")
    missing = [r["key"] for r in rows if not r["name_zh"]]
    print(f"缺中文名: {len(missing)} 张 {missing[:6]}")


if __name__ == "__main__":
    main()
