# 预定义像素坐标

这个目录存放**预先量好并写死**的界面元素坐标, 目的是操作时直接查表点击, 不必每次都截图计算.

## 文件

| 文件 | 内容 |
| --- | --- |
| [positions.json](positions.json) | 机器可读版本, 供脚本直接读取 |
| [main-game.md](main-game.md) | 主游戏界面 (出牌, 弃牌, 理牌, 左侧面板, 手牌区) |
| [shop.md](shop.md) | 商店界面 (下一个回合, 重掷, 商品位, 优惠券位, 补充包位) |
| [cash-out-and-result.md](cash-out-and-result.md) | 盲注结算与提现界面 |

## 坐标系

设备覆盖分辨率 1080x2400, 横屏游戏截图 2400x1080.
表中坐标单位是**横屏截图像素**, 可直接用于:

```shell
adb -s <serial> shell input tap <x> <y>
```

## 使用方式

```python
import json
pos = json.load(open('positions.json'))
x, y = pos['mainGame']['buttons']['play']['tap']
```

`box` 是元素包围盒 `[x0, y0, x1, y1]`, `tap` 是建议点击点 (包围盒中心或目视确认的安全点).
`verified: true` 表示该点已经被实际点击并验证生效.

## 量取方式

1. 截图 (`exec-out screencap`).
2. 叠加 50/100 px 网格后缩放读图, 记录元素包围盒.
3. 用颜色掩码精确求包围盒 (按钮底色都是纯色, 检测稳定):

```python
import numpy as np
from PIL import Image

def bbox(path, region, pred):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    x0, y0, x1, y1 = region
    m = pred(a[y0:y1, x0:x1])
    ys, xs = np.nonzero(m)
    return (x0 + int(xs.min()), y0 + int(ys.min()), x0 + int(xs.max()), y0 + int(ys.max()))

# 出牌按钮 (蓝底, 启用态)
bbox('shot.png', (900, 870, 1350, 1050),
     lambda m: (m[:, :, 2] > 190) & (m[:, :, 0] < 90) & (m[:, :, 1] > 90) & (m[:, :, 1] < 170))
```

4. 画点验证后再写入本目录.

## 已知的坑

- **按钮有启用/禁用两态**: 禁用时整颗按钮是灰色, 用颜色掩码量出来的包围盒会变成文字范围. 量取按钮尺寸必须在**启用状态**下截图, 或改用固定区域目视读.
- **数字 0 带斜杠**: 该字体里 `0` 有一条斜杠, 缩小后容易被看成 `8`. 槽位计数 "0/2" 会误读成 "8/2", 需要放大确认.
- **手牌区不适用固定坐标**: 手牌数量变化时整排牌会重新居中排布. 坐标表只给出 8 张时的位置与通用公式, 数量特殊时仍要读图定位.
- 商店货架的**商品内容**变化, 但**槽位坐标固定**, 因此商店坐标可以写死.
- 分辨率或显示大小被改动后, 全部坐标需要重量. 每次开工先 `wm size` 确认覆盖分辨率.
