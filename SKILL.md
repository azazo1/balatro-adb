---
name: balatro-adb
description: 用 adb 在 Android 设备上操控 Balatro (小丑牌) 等无控件横屏游戏. 覆盖无线连接与多 transport 选择, 截图与坐标系换算, 点击与等待节奏, 缩放裁剪读图, 叠加坐标网格定位元素, 预定义坐标表, 以及 "截图-定位-点击-复查" 的稳定操作循环. 当需要代替手指玩 Balatro, 点击手牌/出牌/弃牌/商店购买, 从截图读取分数与手牌, 或排查 "点了没反应/点错位置" 时使用.
---

# Balatro adb 操控

在 Android 设备上用 adb 代替手指玩 Balatro. 游戏是 Love2D 打包的, **没有 view 层级**,
`uiautomator dump` 拿不到任何控件, 因此整条链路只有两种手段: 看截图, 发点击.

## 何时使用

- 让 agent 自己把一局 Balatro 打下去 (选牌, 出牌, 弃牌, 买牌, 过商店).
- 读取当前局面: 分数线, 回合分数, 剩余出牌/弃牌, 金钱, 手牌点数花色.
- 排查 "点了没反应" 或 "点到隔壁牌": 多半是坐标系或落点问题.

不适用的场景: 需要精确操作 Windows/桌面程序 (用 Computer Use), 或需要从游戏内存读状态 (本技能只做视觉闭环).

## 环境前提

| 项目 | 要求 |
| --- | --- |
| adb | 1.0.41 (37.0.0) 及以上, 已在 PATH |
| 设备 | 已连接并授权 (`adb devices` 显示 `device` 而非 `unauthorized`) |
| 图像处理 | Pillow (缩放裁剪读图, 叠加网格) |
| 设备侧 | 游戏中 (前台窗口含 `GameActivity` 或类似) |

```shell
adb devices -l
# 如果出现两条指向同一台设备的记录 (直连与 mDNS), 所有命令都要带 -s <serial>
```

## 三条最重要的结论

1. **截图坐标 = 点击坐标**. `screencap` 出的图片尺寸与 `input tap` 用的是同一套坐标系,
   以截图上的像素坐标直接点击, 不要按物理分辨率 (`wm size` 的 Physical size) 换算.
2. **横屏截图宽高互换**. 竖屏是 1080x2400, 横屏游戏截图是 **2400x1080**, 点击 x 可到 2399, y 只到 1079.
   按竖屏推算会让点击落到完全无关的位置.
3. **读图前先缩放**. 原图 2400x1080 直接读会浪费上下文又看不清细节; 先缩到 1200-1400 px 宽看全局,
   需要细节再裁剪放大.

## 快速开始

```shell
S=<serial>                                   # 见 adb devices 第一列
adb -s $S exec-out screencap -p > /tmp/shot.png    # 必须 exec-out
sips -Z 900 /tmp/shot.png --out /tmp/small.png      # 缩放后再看
adb -s $S shell input tap 1093 946                  # 出牌按钮
sleep 1
adb -s $S exec-out screencap -p > /tmp/after.png    # 复查
```

判断现在在哪个界面:

```shell
adb -s $S shell dumpsys window | grep mCurrentFocus
```

## 操作循环 (固定五步)

一次可靠的操作是:

1. **截图** `exec-out screencap` 到临时文件.
2. **缩放读全局**: 判断界面 (对局 / 结算 / 提现 / 商店) 与关键数值.
3. **定位落点**: 查 [pos/positions.json](references/adb/pos/positions.json) 拿固定按钮坐标;
   手牌区按公式算; 拿不准就叠加网格读数.
4. **画点验证**: 把要点的坐标画在图上, 目视确认落在目标元素上 (挡住 "点错牌" 这类昂贵错误).
5. **点击 + 复查**: `input tap`, sleep 0.3-0.5 秒 (动画场景 2-3 秒), 重新截图确认状态真的变了.

**只发事件不看结果, 很容易在错误的界面上继续点击, 把局面搞乱.** 每次切换界面都要重新截图.

## 界面与坐标

固定按钮的坐标已经量好写死在 [references/adb/pos/](references/adb/pos/README.md), 直接查表, 不必每次算图:

| 界面 | 文件 | 关键点 |
| --- | --- | --- |
| 主对局 | [pos/main-game.md](references/adb/pos/main-game.md) | 出牌 (1093, 946), 弃牌 (1495, 946), 手牌公式 |
| 商店 | [pos/shop.md](references/adb/pos/shop.md) | 下一个回合 (939, 439), 货架 5 个槽位, **购买是两步** |
| 结算与提现 | [pos/cash-out-and-result.md](references/adb/pos/cash-out-and-result.md) | 继续 (1283, 760), 提现 (1545, 444) |

### 手牌区 (唯一不能用固定表的地方)

手牌数量变化时整排牌会重新居中, 用公式:

```text
点第 i 张牌 (1-based, 共 N 张):
  x = 1220 + (i - (N + 1) / 2) * s     s ≈ 130 (N ≥ 5), 137 (N ≤ 4)
  y = 690
```

8 张牌时实测点击点: `768 898 1027 1156 1285 1414 1543 1672` (y = 690).
选中后卡牌会向上抬起约 44 px, 可以用顶边 y 的变化确认是否真的选中.

## 读图方法

- 全局看: 缩到 1200-1400 px 宽.
- 看细节: 裁剪 + 2-3 倍放大, 注意裁剪框是**原图坐标**, 不要把放大后的像素当坐标.
- 定位不准时: 叠加 50/100 px 网格后读数, 或把候选点画在图上验证.
- 判断选中状态: 比较操作前后同一列的卡牌顶边 y.

细节与可复制代码见 [04-image-read.md](references/adb/04-image-read.md).

## 常见坑

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 截图文件损坏 | 用了 `adb shell screencap -p > file` | 改用 `exec-out`; 偶发截断就重试 (检查文件大小) |
| 提示多个设备 | 同设备有直连与 mDNS 两条 transport | 所有命令加 `-s <serial>` |
| 点击无反应 | 动画没结束, 或点在元素边缘外 | sleep 后重截, 落点取元素中心 |
| 点到相邻的牌 | 手牌扇形重叠, 坐标是估算的 | 查公式或叠网格, 画点验证后再点 |
| 买完发现没扣钱/没到手 | 商店购买是**两步**: 先选中, 再点浮出的 "购买" | 点第二次确认按钮 |
| 把 0 读成 8 | 该字体数字 `0` 带一条斜线, 缩小后易混 | 放大确认 (槽位计数曾把 "0/2" 误读成 "8/2") |
| 认错卡牌 | 靠低分辨率卡面图形认牌, 或者把悬停说明读错 | 读悬停提示的**文字**, 或读游戏数据 (见下) |

## 认牌与查数值: 读游戏自带数据

Balatro 的 APK 里有完整的 Lua 数据 (含官方中文), 比截图可靠得多, 也能解释 "为什么这张牌不触发":

```shell
adb -s $S shell pm path <包名>
adb -s $S pull /data/app/~~xxx/<包名>-xxx/base.apk /tmp/base.apk
unzip -o -q /tmp/base.apk assets/game.love -d /tmp/apk
unzip -o -q /tmp/apk/assets/game.love -d /tmp/game-src
cat /tmp/game-src/version.jkr                 # 游戏版本
grep -n 'j_mad=' /tmp/game-src/game.lua       # 卡牌定义
```

- [scripts/extract_apk_game_data.py](scripts/extract_apk_game_data.py): 提取全部小丑牌的
  价格, 稀有度, 效果配置与官方中文名, 输出 CSV.
- 设备上的版本可能与网上资料不一致 (实测 **1.0.0L** 与 wiki 的 1.0.1o 有 13 张价格, 5 张稀有度,
  以及疯狂小丑/聪慧小丑/旗帜等效果数值的差异), 详见 [references/version-diff.md](references/version-diff.md).

## 参考资料

| 主题 | 文件 |
| --- | --- |
| 连接, 多 transport, 多用户 (分身) | [01-connection.md](references/adb/01-connection.md) |
| 分辨率, 坐标系, 截图, 屏幕方向 | [02-screen.md](references/adb/02-screen.md) |
| 点击, 长按, 滑动, 按键, 等待节奏 | [03-input.md](references/adb/03-input.md) |
| 缩放裁剪读图, 网格读数, 状态检测 | [04-image-read.md](references/adb/04-image-read.md) |
| Balatro 界面布局概览 | [05-balatro-layout.md](references/adb/05-balatro-layout.md) |
| 完整操作循环与坑 | [06-workflow.md](references/adb/06-workflow.md) |
| 预定义像素坐标 (机器可读 + 说明) | [pos/](references/adb/pos/README.md) |
| 游戏版本差异 (1.0.0L vs 1.0.1o) | [version-diff.md](references/version-diff.md) |

### 决策用的游戏规则

打游戏要选牌型, 买什么牌, 算分数线, 因此附了一份完整规则手册 (中文, 按 Balatro Wiki 1.0.1o 整理):

| 主题 | 文件 |
| --- | --- |
| 一局流程, 默认数值, 结算顺序 | [rules/01-run-basics.md](references/rules/01-run-basics.md) |
| 计分公式, 牌型与升级, 计分顺序 | [rules/02-scoring-and-hands.md](references/rules/02-scoring-and-hands.md) |
| 增强 / 版本 / 蜡封 / 贴纸 | [rules/03-card-modifiers.md](references/rules/03-card-modifiers.md) |
| 150 张小丑牌与触发类型 | [rules/04-jokers.md](references/rules/04-jokers.md) |
| 塔罗 / 星球 / 幻灵牌 | [rules/05-consumables.md](references/rules/05-consumables.md) |
| 牌组 / 赌注 / 挑战 | [rules/06-decks-stakes-challenges.md](references/rules/06-decks-stakes-challenges.md) |
| 商店, 价格, 补充包, 优惠券, 金钱 | [rules/07-shop-and-economy.md](references/rules/07-shop-and-economy.md) |
| 盲注效果, 分数要求表, 标签 | [rules/08-blinds-and-tags.md](references/rules/08-blinds-and-tags.md) |
| 无尽模式, 概率, 术语表 | [rules/09-endless-and-appendix.md](references/rules/09-endless-and-appendix.md) |

## 目录结构

```text
SKILL.md                  本文件, 入口
references/adb/           adb 操作细节 (连接/屏幕/输入/读图/布局/循环)
references/adb/pos/       预定义坐标表 (JSON + 说明)
references/rules/         游戏规则手册 (决策参考)
references/version-diff.md  版本差异记录
scripts/                  抓取, 提取, 校验, adb 辅助脚本
data/                     结构化数据 CSV (wiki 版 + 从 APK 提取的 1.0.0L 版)
raw/ txt/                 wiki 原始页面与纯文本 (规则手册的出处)
```

## 已知限制

- 手牌区只能靠公式或网格估算, 没有可靠的自动识别; 牌面点数花色依赖读图.
- 游戏内没有控件树, 所有状态判断都基于截图, 因此**每一步都要复查**.
- 换设备或改动显示大小 (覆盖分辨率变化) 后, `pos/` 里的坐标全部需要重新标定.
