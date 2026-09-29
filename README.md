# Balatro (小丑牌) 规则手册

本目录汇总 Balatro 的完整游戏规则, 内容依据社区维护的 [Balatro Wiki](https://balatrowiki.org/) 整理并翻译,
对应版本 **1.0.1o-FULL (Friends of Jimbo 4)**, 抓取时间 2026-09-29.

## 文档索引

| 文档 | 内容 |
| --- | --- |
| [docs/01-run-basics.md](docs/01-run-basics.md) | 一局的整体流程: 底注, 盲注, 回合, 出牌与弃牌, 手牌, 槽位, 结算 |
| [docs/02-scoring-and-hands.md](docs/02-scoring-and-hands.md) | 计分公式, 13 种牌型的基础分与升级, 牌面筹码 |
| [docs/03-card-modifiers.md](docs/03-card-modifiers.md) | 增强, 版本, 蜡封, 贴纸, 修饰的出现概率与价格 |
| [docs/04-jokers.md](docs/04-jokers.md) | 小丑牌机制与全部 150 张小丑牌 |
| [docs/05-consumables.md](docs/05-consumables.md) | 塔罗牌 22 张, 星球牌 12 张, 幻灵牌 18 张 |
| [docs/06-decks-stakes-challenges.md](docs/06-decks-stakes-challenges.md) | 15 种牌组, 8 个赌注难度, 20 个挑战模式 |
| [docs/07-shop-and-economy.md](docs/07-shop-and-economy.md) | 商店, 价格与售价公式, 补充包, 优惠券, 金钱与利息 |
| [docs/08-blinds-and-tags.md](docs/08-blinds-and-tags.md) | 34 个盲注的效果与底注分数要求, 24 个跳过标签 |
| [docs/09-endless-and-appendix.md](docs/09-endless-and-appendix.md) | 无尽模式, 概率一览, 术语表, 数据来源 |

## 目录结构

- `docs/`: 整理后的中文规则手册.
- `raw/`: 抓取到的 wiki 页面原始 HTML.
- `txt/`: 原始页面转成的纯文本, 便于检索原文.
- `data/`: 从页面中提取的表格 CSV, 是手册中各张表的机器可读版本.
- `scripts/`: 抓取, 提取表格与校验脚本.

## 常用命令

```shell
# 重新抓取 wiki 页面到 raw/ 与 txt/ (需要 curl 与 pandoc)
just fetch

# 从 raw/ 重新提取表格到 data/ (脚本需要 pandas)
just tables

# 校验手册中的小丑牌条目与 wiki 数据是否一致
just check
```

若默认的 `python3` 没有 pandas, 可以通过环境变量指定解释器, 例如:

```shell
PYTHON=/path/to/python just tables
```

## 快速上手

一局游戏 = 挑战 8 个底注 (Ante), 每个底注包含小盲注, 大盲注, Boss 盲注各一场.
每场盲注要求在一个回合内用有限的出牌次数打出足够分数, 分数 = 筹码 × 倍率.
击败底注 8 的 Showdown 盲注即算通关, 之后可继续挑战无尽模式.
细节见 [docs/01-run-basics.md](docs/01-run-basics.md).

## 许可与致谢

- 游戏规则与数值来自社区维护的 [Balatro Wiki](https://balatrowiki.org/), 该站内容以
  [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/) 授权发布.
  `docs/`, `data/`, `raw/`, `txt/` 都是它的翻译, 摘录或再加工, 沿用同一授权, 不得用于商业用途.
- `scripts/` 与 `justfile` 为本仓库自行编写的工具代码.
- Balatro 由 LocalThunk 开发, Playstack 发行; 本仓库与官方无关, 也不包含游戏的美术资源.
- 详细说明见 [NOTICE.md](NOTICE.md).

