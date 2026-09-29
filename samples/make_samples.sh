#!/usr/bin/env bash
# Rebuild the SAMPLE launch boards from fictional demo data (engine -> spec -> PNG at both sizes).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; PY="${PY:-$ROOT/.venv/bin/python}"; [ -x "$PY" ] || PY=python3
B="$ROOT/engine/board.py"; T=$(mktemp -d); OUT="$ROOT/samples"
mk() { export FOUNDER_BOARD="$T/$1.json"; }

# 1) Day 5: fictional candle maker, early days
mk early; $PY $B --today 2026-09-01 init --mission "Juniper & Ash Candle Co." --launch 2026-11-13 >/dev/null
for id in O5 M1 M2 L1 L10; do $PY $B --today 2026-09-05 set $id done >/dev/null; done
$PY $B --today 2026-09-05 set L2 doing >/dev/null
$PY $B --today 2026-09-05 set L3 waiting --note "owner filing" >/dev/null
$PY $B --today 2026-09-06 spec --out "$OUT/specs/sample-early.json"

# 2) Mid-flight: fictional coffee roaster
mk mid; $PY $B --today 2026-08-01 init --mission "Fieldnote Coffee Roasters" --launch 2026-10-23 >/dev/null
for id in O5 M1 M2 L1 L2 L10 L3 L5 L4 L6 L7 S1 L8 A1 A3 O2; do $PY $B --today 2026-09-10 set $id done >/dev/null; done
for id in L9 A2 A4 S2; do $PY $B --today 2026-09-26 set $id done >/dev/null; done
$PY $B --today 2026-09-26 set S3 doing >/dev/null
$PY $B --today 2026-09-28 spec --out "$OUT/specs/sample-mid.json"

# 3) Stealth mode (anonymous codename), almost at liftoff
mk stealth; $PY $B --today 2026-07-01 init --mission "Hidden Brand" --codename "Project Nightjar" --launch 2026-10-02 >/dev/null
for id in $($PY -c "import json;print(' '.join(t['id'] for t in json.load(open('$FOUNDER_BOARD'))['tasks']))"); do
  case $id in M6|A6|S7) ;; *) $PY $B --today 2026-09-15 set $id done >/dev/null;; esac; done
for id in S7 A6; do $PY $B --today 2026-09-26 set $id done >/dev/null; done
$PY $B --today 2026-09-28 spec --anonymous --out "$OUT/specs/sample-stealth.json"

# 4) LIFTOFF: fictional soap maker, every item GO on launch day
mk liftoff; $PY $B --today 2026-08-03 init --mission "Tidewater Soap Works" --launch 2026-09-28 >/dev/null
for id in $($PY -c "import json;print(' '.join(t['id'] for t in json.load(open('$FOUNDER_BOARD'))['tasks']))"); do
  case $id in M5|S7|A6) ;; *) $PY $B --today 2026-09-10 set $id done >/dev/null;; esac; done
for id in M5 S7 A6; do $PY $B --today 2026-09-24 set $id done >/dev/null; done
$PY $B --today 2026-09-28 spec --out "$OUT/specs/sample-liftoff.json"

for f in "$OUT"/specs/sample-*.json; do $PY "$ROOT/board/render.py" "$f" --out "$OUT" --sample; done
