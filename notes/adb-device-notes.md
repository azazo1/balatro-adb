# adb 操作笔记 (小米 23013RK75C / mondrian, 1440x3200)

用于记录通过 adb 操控这台设备时的实测结论, 尤其是坐标与分辨率相关的坑.

## 设备与连接

| 项目 | 值 |
| --- | --- |
| adb 版本 | 1.0.41 (37.0.0), 路径 `~/Library/Android/sdk/platform-tools/adb` |
| 型号 | `23013RK75C`, product/device 均为 `mondrian` |
| 连接方式 | 同一设备同时出现两个 transport: `192.168.1.104:41495` 与 `adb-<hash>._adb-tls-connect._tcp` |
| 系统 | MIUI, 主用户 id 0 (机主), 另有 user 999 (`XSpace` 分身, 已运行) |

多 transport 时要显式指定设备, 否则 adb 报 `more than one device/emulator`:

```shell
adb -s 192.168.1.104:41495 shell ...
```

## 分辨率与坐标系

这是最容易出错的地方, 结论如下:

| 来源 | 数值 |
| --- | --- |
| `wm size` 物理尺寸 | 1440x3200 (竖屏) |
| `wm size` 覆盖尺寸 | 1080x2400 (竖屏, Override) |
| `screencap` 竖屏截图 | 1080x2400 |
| `screencap` 横屏截图 (游戏内) | **2400x1080** |
| `input tap` 坐标范围 | 跟随覆盖分辨率, 横屏时即 x 0-2399, y 0-1079 |

要点:

- 截图分辨率和 `input tap` 的坐标系是同一套, 所以**以截图上的像素坐标直接 tap 即可**, 不需要按物理尺寸换算.
- 横屏应用的截图宽高是交换的 (2400x1080), 不要按竖屏的 1080x2400 推算.
- 读取截图前先缩放 (`sips -Z 900` 或 Pillow 缩放), 避免直接读原图撑爆上下文.

## 截图与读取

```shell
S=192.168.1.104:41495
adb -s $S exec-out screencap -p > /tmp/shot.png     # 用 exec-out, 勿用 shell 重定向 (会破坏二进制)
sips -Z 900 /tmp/shot.png --out /tmp/shot-small.png  # 缩放后再读图
```

在 macOS 上 `adb shell screencap -p > file` 会因换行符转换损坏 PNG, 必须用 `exec-out`.

## 前台应用查询

```shell
adb -s $S shell dumpsys window | grep mCurrentFocus
# 游戏: org.bal6tro.android/org.love2d.android.GameActivity (Love2D 打包)
```

Love2D 打包的游戏界面**没有 view 层级**, `uiautomator dump` 拿不到控件, 只能靠截图 + 固定坐标点击.

## 点击

```shell
adb -s $S shell input tap <x> <y>              # 坐标见上, 横屏即截图坐标
adb -s $S shell input swipe <x1> <y1> <x2> <y2> <ms>
```

- 点击后建议 sleep 0.3-0.5 秒再截图, 游戏有动画.
- 连续点击用循环即可, 但每次都要重新截图确认状态, 因为画面会变.

## Balatro 横屏 2400x1080 的界面坐标 (实测)

| 元素 | 坐标 (点击点) |
| --- | --- |
| 出牌按钮 | (1080, 940) |
| 弃牌按钮 | (1512, 940) |
| 按点数排序 | (1250, 940) |
| 按花色排序 | (1360, 940) |

手牌扇形区大致位于 x 760-1900, y 600-800; 牌堆在右侧 x ~1930, y ~810; 左侧信息面板 x 180-460.

> 手牌是带旋转的扇形排列, 牌与牌互相重叠, 不能用"等间距"推算坐标. 正确做法是给截图叠加坐标网格后目视读数, 见下面的流程.

## 给截图叠加网格读数

```python
from PIL import Image, ImageDraw
im = Image.open('/tmp/shot.png').convert('RGB')
d = ImageDraw.Draw(im)
for x in range(0, im.width, 50):
    d.line([(x, 0), (x, im.height)], fill=(255, 0, 255), width=1)
    d.text((x + 2, 4), str(x), fill=(255, 0, 255))
for y in range(0, im.height, 50):
    d.line([(0, y), (im.width, y)], fill=(0, 255, 255), width=1)
    d.text((4, y + 2), str(y), fill=(0, 255, 255))
im.save('/tmp/grid.png')
```

读数时把网格图缩放到 1000-1200 px 宽再读, 避免超大图.

## 待办与经验

- [ ] 手牌点选的稳妥方式: 目前靠网格读坐标, 可通过"顶点/台阶检测"自动化, 但扇形旋转小, 台阶检测不稳定, 需继续验证.
- 弃牌与出牌的确认按钮固定, 只有手牌区需要精确坐标.
