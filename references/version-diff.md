# 设备上的游戏数据 (1.0.0L) 与 wiki (1.0.1o) 的差异

## 起因

用 adb 操作设备上的 Balatro 时, 悬停工具提示显示 "疯狂小丑: 如果出牌中包含**四条** +20 倍率",
而手册 (依据 Balatro Wiki 1.0.1o-FULL) 里 Mad Joker 是 "包含**两对** +10 倍率".

## 取证方法

APK 是 world-readable 的, 可以直接拉出来读它自带的 Lua 数据 (无需 root):

```shell
# 1. 找到 APK 路径 (注意这是第三方包名, 不是官方 com.playstack.balatro.android)
adb -s <serial> shell pm path <包名>
# 2. 拉取
adb -s <serial> pull /data/app/~~xxx==/<包名>-xxx==/base.apk /tmp/balatro-base.apk
# 3. 逐层解包: APK -> assets/game.love -> Love2D 源码
unzip -o -q /tmp/balatro-base.apk assets/game.love -d /tmp/game-love-apk
unzip -o -q /tmp/game-love-apk/assets/game.love -d /tmp/game-love-src
```

解出来的目录里有 `game.lua` (全部卡牌定义), `version.jkr` (游戏版本), `localization/zh_CN.lua` (官方中文).

小丑牌定义形如:

```lua
j_mad = {order = 8, ..., rarity = 1, cost = 4, name = "Mad Joker", ...,
         config = {t_mult = 20, type = 'Four of a Kind'}},
```

`t_mult` / `t_chips` 是数值, `type` 是触发条件牌型, rarity 数字 1-4 对应 普通/不常见/稀有/传奇.

## 版本

| | 设备上的游戏 | wiki (手册依据) |
| --- | --- | --- |
| `version.jkr` | 1.0.0L-FULL (Console_other) | 1.0.1o-FULL |
| 小丑牌条目 | 151 | 150 |

两者不是同一版本, 因此数据本来就不该完全一致.

## 具体差异

### 效果数值

| 小丑牌 | 设备 (1.0.0L) | wiki (1.0.1o) |
| --- | --- | --- |
| 欢乐小丑 Jolly | +8 倍率, 对子 | 同 |
| 滑稽小丑 Zany | +12 倍率, 三条 | 同 |
| **疯狂小丑 Mad** | **+20 倍率, 四条** | +10 倍率, 两对 |
| 癫狂小丑 Crazy | +12 倍率, 顺子 | 同 |
| 诙谐小丑 Droll | +10 倍率, 同花 | 同 |
| 狡黠小丑 Sly | +50 筹码, 对子 | 同 |
| 狡猾小丑 Wily | +100 筹码, 三条 | 同 |
| **聪慧小丑 Clever** | **+150 筹码, 四条** | +80 筹码, 两对 |
| 刁钻小丑 Devious | +100 筹码, 顺子 | 同 |
| 灵巧小丑 Crafty | +80 筹码, 同花 | 同 |
| 旗帜 Banner | 每次剩余弃牌 +40 筹码 | +30 筹码 |

### 价格 (13 张不同, 例)

| 小丑牌 | 设备 | wiki |
| --- | --- | --- |
| 斐波那契 Fibonacci | $7 | $8 |
| 方块小丑 Square Joker | $5 | $4 |
| 流浪汉 Vagabond | $6 | $8 |
| 云 9 Cloud 9 | $6 | $7 |
| 迈达斯面具 Midas Mask | $6 | $7 |
| 交易卡 Trading Card | $5 | $6 |
| 特技演员 Stuntman | $6 | $7 |
| 隐形小丑 Invisible Joker | $10 | $8 |
| 烧焦小丑 Burnt Joker | $6 | $8 |

### 稀有度 (5 张不同)

| 小丑牌 | 设备 | wiki |
| --- | --- | --- |
| 第六感 Sixth Sense | 稀有 | 不常见 |
| 流浪汉 Vagabond | 不常见 | 稀有 |
| 专属车位 Reserved Parking | 不常见 | 普通 |
| 特技演员 Stuntman | 不常见 | 稀有 |
| 烧焦小丑 Burnt Joker | 不常见 | 稀有 |

### 名称拼写

设备: `Caino`, `Riff-raff`, `Seance`; wiki: `Canio`, `Riff-Raff`, `Séance`.

## 结论与做法

- 手册按 **1.0.1o-FULL** 写, 与设备上的 **1.0.0L** 存在上述差异, 属于版本差异, 不是 wiki 写错.
- 需要给这台设备用的话, 应以 APK 里的 `game.lua` 为准重新生成小丑牌表.
- `localization/zh_CN.lua` 是官方简体中文, 其中的卡牌名可以替换手册里自行意译的中文名.
- 设备上装的包名不是官方包名, 但内部数据与 Love2D 结构完整 (含官方中文档), 属于第三方重打包的 1.0.0L 构建.

## 教训

不要靠低分辨率的卡面图形认牌. 判断一张牌是什么, 优先看悬停说明 (`带名称 + 效果文本`), 或者直接读游戏数据.
本次连续两次判断失误: 先按 wiki 推断效果, 又把 Mad Joker 认成基础 Joker.
