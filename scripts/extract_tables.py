#!/usr/bin/env python3
"""从 raw/ 中的 wiki HTML 提取所有表格, 输出为 data/ 下的 CSV.

用法: python3 scripts/extract_tables.py
"""

import pathlib
import re

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
OUT = ROOT / "data"


def clean(cell: object) -> object:
    """去掉单元格里的 HTML 标签与多余空白."""
    if not isinstance(cell, str):
        return cell
    text = re.sub(r"<[^>]+>", " ", cell)
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for html in sorted(RAW.glob("*.html")):
        try:
            tables = pd.read_html(html)
        except Exception as exc:  # noqa: BLE001
            # 没有表格的页面 (或解析器缺失的表格) 跳过, 纯文本仍在 txt/ 中.
            print(f"{html.stem}: 跳过 ({exc})")
            continue
        for i, table in enumerate(tables):
            table = table.map(clean)
            path = OUT / f"{html.stem}.{i}.csv"
            table.to_csv(path, index=False)
        sizes = ", ".join(f"{i}:{t.shape[0]}x{t.shape[1]}" for i, t in enumerate(tables))
        print(f"{html.stem}: {len(tables)} 张表 -> {sizes}")


if __name__ == "__main__":
    main()
