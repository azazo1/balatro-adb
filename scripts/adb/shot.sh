#!/usr/bin/env bash
# 截图到文件, 遇截断自动重试, 可选缩放.
#
# 用法:
#   scripts/adb/shot.sh [输出路径] [缩放后长边像素]
#   scripts/adb/shot.sh /tmp/shot.png 1200
#
# 设备通过 ADB_SERIAL 指定; 未设置时, 若只有一台设备则自动使用.
set -euo pipefail

out="${1:-/tmp/dsh-adb-shot.png}"
scale_to="${2:-}"

: "${ADB_SERIAL:=$(adb devices | awk 'NR>1 && $2 == "device" {print $1; exit}')}"
if [ -z "${ADB_SERIAL}" ]; then
    echo "没有可用设备: 检查 adb devices 是否有状态为 device 的设备" >&2
    exit 1
fi
export ADB_SERIAL

# 截图偶发截断 (文件过小), 重试几次
for attempt in 1 2 3 4; do
    adb -s "${ADB_SERIAL}" exec-out screencap -p > "${out}"
    size=$(wc -c < "${out}" | tr -d ' ')
    if [ "${size}" -gt 50000 ]; then
        break
    fi
    echo "第 ${attempt} 次截图仅 ${size} 字节, 重试" >&2
    sleep 1
done

if [ "${size:-0}" -le 50000 ]; then
    echo "截图失败: 文件只有 ${size} 字节, 设备可能处于锁屏或传输中断" >&2
    exit 1
fi

printf '%s (%s 字节)\n' "${out}" "${size}"

if [ -n "${scale_to}" ]; then
    scaled="${out%.png}-small.png"
    if command -v sips >/dev/null 2>&1; then
        sips -Z "${scale_to}" "${out}" --out "${scaled}" >/dev/null
    else
        python3 -c "from PIL import Image; im = Image.open('${out}'); \
            r = ${scale_to} / max(im.size); im.resize((int(im.width*r), int(im.height*r)), Image.LANCZOS).save('${scaled}')"
    fi
    printf '%s (缩放到长边 %s px)\n' "${scaled}" "${scale_to}"
fi
