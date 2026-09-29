# 来源, 授权与免责

## 内容来源

本仓库的全部游戏规则, 数值与列表整理自社区维护的 [Balatro Wiki](https://balatrowiki.org/):

- `raw/`: 抓取到的 wiki 页面原始 HTML.
- `txt/`: 上述页面转成的纯文本.
- `data/`: 从上述页面提取的表格 CSV.
- `docs/`, `README.md`: 基于上述内容整理与翻译的中文手册.

对应游戏版本 **1.0.1o-FULL (Friends of Jimbo 4)**, 抓取时间为 **2026-09-29**.
涉及的 wiki 页面清单见 [scripts/fetch-pages.sh](scripts/fetch-pages.sh).

## 授权

Balatro Wiki 的文本内容以
[Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported](https://creativecommons.org/licenses/by-nc-sa/3.0/)
(CC BY-NC-SA 3.0) 授权发布. 因此:

- `raw/`, `txt/`, `data/`, `docs/` 以及 `README.md` 中的规则内容属于该授权下的衍生作品,
  使用时须署名 Balatro Wiki, 不得用于商业目的, 并以相同方式共享.
- `scripts/` 与 `justfile` 是仓库自行编写的工具代码, 可以自由使用于任何目的.
- 本仓库不包含游戏本体, 也不包含游戏美术, 音频等素材.

## 免责声明

- Balatro 由 LocalThunk 开发, Playstack 发行, 相关名称与内容的权利归其所有者.
- 本仓库是非官方的玩家整理, 与开发商, 发行商以及 Balatro Wiki 官方均无关联.
- 手册中的中文译名多为按效果意译, 与游戏内置简体中文版的译名可能不同, 表内均附英文原名便于对照.
- 游戏版本更新后规则可能变化, 请以游戏内实际表现为准; 可通过 `just fetch` 与 `just tables` 重新同步数据.
