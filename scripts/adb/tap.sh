#!/usr/bin/env bash
# 连续点击一串坐标, 每个点之间自动停顿.
#
# 用法:
#   scripts/adb/tap.sh 1093 946                      # 点一个点
#   scripts/adb/tap.sh 768 690 898 690 1027 690      # 依次点三个点
#   TAP_DELAY=1.5 scripts/adb/tap.sh 1283 760        # 改停顿秒数 (默认 0.4)
#
# 设备通过 ADB_SERIAL 指定; 未设置时, 若只有一台设备则自动使用.
set -euo pipefail

if [ "$#" -lt 2 ] || [ $(( $# % 2 )) -ne 0 ]; then
    echo "用法: $0 <x> <y> [<x> <y> ...]" >&2
    exit 1
fi

: "${ADB_SERIAL:=$(adb devices | awk 'NR>1 && $2 == "device" {print $1; exit}')}"
if [ -z "${ADB_SERIAL}" ]; then
    echo "没有可用设备: 检查 adb devices 是否有状态为 device 的设备" >&2
    exit 1
fi

delay="${TAP_DELAY:-0.4}"

while [ "$#" -ge 2 ]; do
    x="$1"; y="$2"; shift 2
    adb -s "${ADB_SERIAL}" shell input tap "${x}" "${y}"
    printf '点击 (%s, %s)\n' "${x}" "${y}"
    if [ "$#" -ge 2 ]; then
        sleep "${delay}"
    fi
done
