#!/usr/bin/env bash
# 从 Balatro Wiki 抓取规则相关页面, 保存到 raw/, 并转成纯文本到 txt/.
# 依赖 curl 与 pandoc. 工作目录固定为仓库根目录.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
mkdir -p raw txt

base="https://balatrowiki.org/w"
pages=(
  Poker_hands Card_modifiers Jokers Decks Stakes Blinds_and_Antes The_Shop Tags
  Booster_Packs Vouchers Tarot_cards Planet_cards Spectral_cards Interest Chips Mult
  Hands Discards Hand_size Joker_slot Consumable_slot Skip Negative_Effects
  Activation_Type Activation_Sequence Listed_probability Money Endless_Mode Rarity
  Challenges Collection
)

for page in "${pages[@]}"; do
  if curl -sfL "$base/$page" -o "raw/$page.html"; then
    pandoc -f html -t plain --wrap=none "raw/$page.html" -o "txt/$page.txt"
    printf '%-22s %s 字节\n' "$page" "$(wc -c < "raw/$page.html" | tr -d ' ')"
  else
    printf '%-22s 抓取失败\n' "$page" >&2
    exit 1
  fi
done

echo "完成, 共 ${#pages[@]} 个页面"
