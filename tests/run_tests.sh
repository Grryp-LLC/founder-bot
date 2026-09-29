#!/usr/bin/env bash
# End-to-end tests: board engine, deadlines + quiet rule, privacy gate, card renders at both sizes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; PY="${PY:-$ROOT/.venv/bin/python}"; [ -x "$PY" ] || PY=python3
T=$(mktemp -d); B="$ROOT/engine/board.py"; export FOUNDER_BOARD=$T/board.json
echo "1) init seeds the plan"
$PY $B --today 2026-10-01 init --mission "Test Goods" --launch 2026-11-26 >/dev/null
$PY -c "import json;b=json.load(open('$T/board.json'));assert len(b['tasks'])==34,len(b['tasks']);assert all(t['due'] for t in b['tasks']);print('   ok: 34 tasks, all dated')"
echo "2) set / skip / add update counts"
$PY $B --today 2026-10-02 set L1 done >/dev/null; $PY $B --today 2026-10-02 set O3 skipped >/dev/null
$PY $B add --area legal --title "Cottage permit check" --needs-yes --due 2026-10-20 >/dev/null
$PY $B --today 2026-10-03 spec --out $T/s.json >/dev/null
$PY -c "import json;s=json.load(open('$T/s.json'));assert s['done']==1 and s['total']==34,s;assert s['days_to_launch']==54;print('   ok: 1/34 (skip excluded, add included), T-54')"
echo "3) deadlines: quiet when nothing due, loud when overdue"
$PY $B --today 2026-10-01 deadlines --within 0 | grep -q QUIET && echo "   ok: quiet"
$PY $B --today 2026-12-01 deadlines --within 3 | grep -q "overdue" && echo "   ok: overdue flagged"
echo "4) weekly review runs"
$PY $B --today 2026-10-05 review | grep -q "Wins this week (1)" && echo "   ok"
echo "5) privacy gate blocks leaks"
for bad in '"mission":"Budget $5,000 Co"' '"mission":"EIN 12-3456789"' '"mission":"Mail me at a@b.com"' '"mission":"Jane Doe Studio","deny_names":["Jane Doe"]' '"mission":"12 Main St Shop"'; do
  echo "{\"type\":\"launch-board\",$bad,\"launch_label\":\"Nov 1, 2026\",\"days_to_launch\":3,\"stages\":[],\"done\":0,\"total\":1,\"next\":[],\"wins_week\":0,\"week_label\":\"Week of Oct 1\"}" > $T/leak.json
  set +e; $PY "$ROOT/board/render.py" $T/leak.json --out $T/leak >/dev/null 2>&1; rc=$?; set -e
  [ $rc -eq 2 ] || { echo "   FAIL: rendered $bad"; exit 1; }
done; echo "   ok: 5 leaks refused"
echo "6) render both sizes (normal + stealth)"
$PY $B --today 2026-10-03 spec --anonymous --out $T/stealth.json >/dev/null
$PY "$ROOT/board/render.py" $T/s.json --out $T/r --sample >/dev/null
$PY "$ROOT/board/render.py" $T/stealth.json --out $T/r >/dev/null
$PY - <<PY
from PIL import Image;import glob,json
fs=sorted(glob.glob("$T/r/*.png"));assert len(fs)==4,fs
for f in fs:
    assert Image.open(f).size in [(1200,675),(1080,1350)],f
assert json.load(open("$T/stealth.json"))["mission"]=="Project Stealth"
print("   ok:",len(fs),"PNGs at X sizes; stealth hides the brand")
PY
echo "ALL TESTS PASSED"
