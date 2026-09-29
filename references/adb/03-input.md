# 输入操作

环境: adb 1.0.41 (37.0.0).

## 点击

```shell
adb -s <serial> shell input tap <x> <y>
```

坐标使用覆盖分辨率那一套 (见 [02-screen.md](02-screen.md)); 横屏应用即用截图上的像素坐标.

连续点击时每次之间要留停顿, 游戏有动画和输入去抖:

```shell
S=<serial>
tap(){ adb -s "$S" shell input tap "$1" "$2"; sleep 0.35; }
tap 773 690
tap 898 690
```

0.3-0.5 秒对大多数界面够用; 涉及翻牌, 计分动画的场景要 1-3 秒.

## 长按

没有独立的 longpress 命令, 用极短的 swipe 代替:

```shell
adb -s <serial> shell input swipe <x> <y> <x> <y> 800   # 原地停 800ms = 长按
```

## 滑动 / 拖拽

```shell
adb -s <serial> shell input swipe <x1> <y1> <x2> <y2> <duration_ms>
```

`duration_ms` 越小越快; 拖拽类操作 (拖卡牌) 需要用 300-800ms 的中等速度, 太快会被识别成甩动.

## 按键

```shell
adb -s <serial> shell input keyevent 4     # BACK
adb -s <serial> shell input keyevent 3     # HOME
adb -s <serial> shell input keyevent 26    # 电源
adb -s <serial> shell input keyevent 82    # 菜单
```

游戏内的 "返回 / 继续" 多数情况下直接点击画面更快, 不要依赖 BACK, 因为游戏可能不处理返回键.

## 文本输入

```shell
adb -s <serial> shell input text 'hello%sworld'   # 空格写成 %s
```

只对真正接受文本输入的应用有效; 游戏一般不适用.

## 启动与关闭应用

```shell
adb -s <serial> shell monkey -p <包名> -c android.intent.category.LAUNCHER 1
adb -s <serial> shell am force-stop <包名>
```

启动后要等应用真正进入前台再开始点击:

```shell
until adb -s <serial> shell dumpsys window | grep -q '<包名>'; do sleep 1; done
```

## 慎用

- `input tap` 只发送事件, **不会** 自动等待界面稳定, 点击后立刻截图常常截到动画中间态, 需要显式 sleep.
- 不要在游戏切场动画期间连点, 容易误触到不想要的按钮 (例如把 "弃牌" 点成 "出牌").
