# 屏幕与坐标系

## 分辨率

```shell
adb -s <serial> shell wm size
```

输出示例:

```text
Physical size: 1440x3200     # 物理分辨率 (竖屏)
Override size: 1080x2400     # 系统覆盖后的分辨率 (竖屏)
```

设备原生是 1440x3200, 但系统把逻辑分辨率覆盖成了 1080x2400.
**`input` 系列命令使用的是覆盖后的坐标系**, 也就是 1080x2400 这一套 (竖屏时).

## 截图尺寸

```shell
adb -s <serial> exec-out screencap -p > shot.png
```

| 场景 | 截图尺寸 |
| --- | --- |
| 竖屏 (桌面等) | 1080x2400 |
| 横屏 (横屏游戏) | 2400x1080 |

即截图尺寸 = 覆盖分辨率的宽高, 横屏时宽高互换.

## 关键结论

截图上的像素坐标可以直接用作 `input tap` 的坐标:

- 两者都基于覆盖分辨率, 不需要按物理分辨率 (1440x3200) 做任何缩放换算.
- 横屏应用的截图是 2400x1080, 因此点击坐标的 x 允许到 2399, y 允许到 1079.
  不要按竖屏的 1080x2400 去推算, 否则点击会落在完全无关的位置.
- 如果系统改过分辨率或显示大小, 覆盖尺寸会变, 坐标表需要重新标定. 每次开工先跑一次 `wm size`.

## 屏幕状态

```shell
adb -s <serial> shell dumpsys window | grep mCurrentFocus   # 当前焦点窗口
adb -s <serial> shell dumpsys window | grep mFocusedApp    # 当前焦点 Activity
```

横屏游戏通常表现为 `<包名>/<引擎的 Activity>`, 例如 Love2D 打包的游戏是
`<包名>/org.love2d.android.GameActivity`.

## 屏幕方向锁

```shell
adb -s <serial> shell settings get system user_rotation      # 0/1/2/3
adb -s <serial> shell settings put system accelerometer_rotation 0   # 锁定自动旋转
adb -s <serial> shell settings put system user_rotation 1            # 1 = 横屏
```

一般不需要手动改, 交给应用自己切换; 只有截图方向不对时才考虑.
