#!/usr/bin/env bash
# Founder Bot kit installer: fonts (pinned + checksummed), Python venv, a headless browser, self-test.
# Safe to re-run. Never touches board.json.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"; cd "$ROOT"
GF_COMMIT="23e54b51ddffbc7713c583748e3bd86f62b1fa4a"
echo "==> fonts"
while read -r name sha src; do
  case "$name" in ''|\#*) continue;; esac
  f="board/fonts/$name"
  if [ ! -f "$f" ] || [ "$(sha256sum "$f" | cut -c1-64)" != "$sha" ]; then
    curl -fsSL "https://raw.githubusercontent.com/google/fonts/$GF_COMMIT/$src" -o "$f.tmp"
    got="$(sha256sum "$f.tmp" | cut -c1-64)"
    [ "$got" = "$sha" ] || { echo "checksum mismatch for $name"; rm -f "$f.tmp"; exit 1; }
    mv "$f.tmp" "$f"
  fi
  echo "   ok $name"
done < board/fonts/fonts.lock
echo "==> python venv"
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip >/dev/null
.venv/bin/pip install -q playwright pillow
echo "==> browser"
if [ -n "${CHROME_PATH:-}" ] || command -v google-chrome >/dev/null || command -v chromium >/dev/null || command -v chromium-browser >/dev/null; then
  echo "   using system Chrome/Chromium"
else
  .venv/bin/playwright install chromium
  echo "   installed Playwright Chromium"
fi
mkdir -p "$HOME/founder-bot/docs" "$HOME/founder-bot/cards"
chmod +x tests/run_tests.sh samples/make_samples.sh
if [ "${SKIP_TESTS:-0}" != "1" ]; then echo "==> self-test"; ./tests/run_tests.sh; fi
echo "Founder Bot kit ready in $ROOT"
