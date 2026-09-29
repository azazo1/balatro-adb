# adb 操控笔记

记录用 adb 操作 Android 设备的实测做法, 以 Balatro (横屏游戏) 为样本.

## 文件索引

| 文件 | 内容 |
| --- | --- |
| [01-connection.md](01-connection.md) | 连接与设备选择, 多 transport 的处理 |
| [02-screen.md](02-screen.md) | 分辨率, 截图, 坐标系的对应关系 |
| [03-input.md](03-input.md) | 点击, 滑动, 按键与等待节奏 |
| [04-image-read.md](04-image-read.md) | 缩放与裁剪读图, 叠加坐标网格读数 |
| [05-balatro-layout.md](05-balatro-layout.md) | Balatro 界面布局概览与元素分布 |
| [06-workflow.md](06-workflow.md) | 一整套 "截图-定位-点击-复查" 的操作循环 |
| [pos/](pos/README.md) | **预定义像素坐标**, 操作时直接查表, 不必每次算图 |

环境: adb 1.0.41 (37.0.0), Android 设备一台横屏应用.

## 三条最重要的结论

1. `screencap` 的图片尺寸与 `input tap` 的坐标是同一套, 直接按截图上的像素坐标点击, 不要按物理分辨率换算.
2. 横屏应用截图是宽高交换的 (2400x1080), 不是竖屏的 1080x2400.
3. 没有 view 层级的应用 (Love2D, Unity, 游戏等) 用不了 `uiautomator`, 只能截图 + 固定坐标点击, 因此维护了 [pos/](pos/README.md) 坐标表.
