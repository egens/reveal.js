#!/usr/bin/env bash
# Создаёт папку презентации из заготовки: index.html, otp.css, логотип.
# Использование: new_deck.sh <папка>
# reveal.js подключается с cdnjs, поэтому папка может лежать где угодно.
set -euo pipefail

if [ $# -ne 1 ]; then
	echo "usage: $0 <deck-dir>" >&2
	exit 1
fi

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DECK="$1"

if [ -e "$DECK/index.html" ]; then
	echo "$DECK/index.html already exists, not overwriting" >&2
	exit 1
fi

mkdir -p "$DECK/img"
cp "$SKILL_DIR/assets/skeleton.html" "$DECK/index.html"
cp "$SKILL_DIR/assets/otp.css" "$DECK/otp.css"
cp "$SKILL_DIR/assets/img/otp-logo.png" "$DECK/img/otp-logo.png"
echo "created $DECK/index.html — replace {{TITLE}}, {{SUBTITLE}}, {{TEAM}}, {{DATE}}"
