# 连接与设备选择

环境: adb 1.0.41 (37.0.0).

## 查看设备

```shell
adb devices -l
```

输出示例 (同一台设备出现两条记录):

```text
List of devices attached
<host>:<port>                       device product:mondrian model:23013RK75C device:mondrian
adb-<hash>-<random>._adb-tls-connect._tcp device product:mondrian model:23013RK75C device:mondrian
```

无线调试会同时暴露两个 transport: 一个是 `host:port` 的直连, 一个是 mDNS 的 TLS 连接.
它们指向同一台设备, 但 adb 认为这是两个设备.

## 指定设备

只要设备数大于 1, 所有命令都必须带 `-s`, 否则报 `more than one device/emulator`:

```shell
adb -s <serial> shell getprop ro.product.model
```

`<serial>` 用 `adb devices` 第一列的原样字符串 (含端口或 `_adb-tls-connect` 后缀).

## 常用确认命令

```shell
adb -s <serial> shell getprop ro.product.model      # 型号
adb -s <serial> shell getprop ro.build.version.release  # Android 版本
adb -s <serial> shell pm list users                 # 用户空间 (含分身)
adb -s <serial> shell wm size                       # 屏幕分辨率
adb -s <serial> shell dumpsys window | grep mCurrentFocus  # 当前前台窗口
```

## 多用户 (分身)

部分系统有独立用户空间 (例如厂商的 "分身" 空间). 默认命令只作用于主用户:

```shell
adb -s <serial> shell pm list packages --user <id> -3   # 指定用户下的第三方应用
```

排查 "应用明明装了却找不到包名" 时, 先确认它装在哪个用户下.

## 保持连接

- 无线连接偶尔会掉, 重新 `adb connect <host>:<port>` 即可.
- 断线后 transport id 会变, 脚本里不要缓存 transport id.
