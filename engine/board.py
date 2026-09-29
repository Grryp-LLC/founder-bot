#!/usr/bin/env python3
"""Founder Bot launch board: a small JSON task tracker with deadlines, weekly review, and card specs.

  board.py init --mission "Brand" --launch YYYY-MM-DD [--codename "Project X"] [--areas legal,store]
  board.py show [--area legal]          board.py next [--n 5]
  board.py set ID STATUS [--note ..] [--due YYYY-MM-DD] [--source URL]
  board.py add --area store --title ".." [--due ..] [--needs-yes] [--source URL]
  board.py deadlines [--within 14] [--json]      board.py review
  board.py spec [--anonymous] --out spec.json

STATUS: todo | doing | waiting | done | skipped. "waiting" = waiting on the owner (a yes, a signature, a filing).
Board file: $FOUNDER_BOARD or ~/founder-bot/board.json. --today YYYY-MM-DD overrides the date (tests).
This tool only tracks. It never spends money, files, submits, or sends anything.
"""
import argparse, json, os, sys
from datetime import date, timedelta
from pathlib import Path

AREAS = [("legal", "LEGAL"), ("store", "STORE"), ("marketing", "MARKETING"), ("money", "MONEY"), ("ops", "OPS")]
PREFIX = {"legal": "L", "store": "S", "marketing": "M", "money": "A", "ops": "O"}
STATUSES = ("todo", "doing", "waiting", "done", "skipped")
# (id, area, title, needs_owner_yes, share of the runway at which it is due)
LIBRARY = [
    ("L1", "legal", "Choose entity type", False, .10),
    ("L2", "legal", "Check name availability in your state", False, .10),
    ("L3", "legal", "File formation with the state", True, .20),
    ("L4", "legal", "Get an EIN from the IRS", True, .25),
    ("L5", "legal", "Pick a registered agent", False, .20),
    ("L6", "legal", "Draft and sign operating agreement", True, .30),
    ("L7", "legal", "Open business bank account", True, .30),
    ("L8", "legal", "Check licenses and permits", False, .35),
    ("L9", "legal", "Register for sales tax", True, .45),
    ("L10", "legal", "Trademark knockout search", False, .20),
    ("S1", "store", "Pick a selling platform", False, .25),
    ("S2", "store", "Work the store setup checklist", False, .50),
    ("S3", "store", "Draft first product listings", False, .55),
    ("S4", "store", "Connect payments", True, .60),
    ("S5", "store", "Set shipping rates and packaging", False, .60),
    ("S6", "store", "Draft returns, privacy, and terms", False, .60),
    ("S7", "store", "Run a test order end to end", False, .85),
    ("M1", "marketing", "Brand and positioning worksheet", False, .15),
    ("M2", "marketing", "Check domain and social handles", False, .15),
    ("M3", "marketing", "Set up email list and signup form", False, .55),
    ("M4", "marketing", "Draft 30 days of social posts", False, .70),
    ("M5", "marketing", "Write the launch-day plan", False, .75),
    ("M6", "marketing", "Plan a small ad test", True, .90),
    ("A1", "money", "Pick a bookkeeping tool", False, .35),
    ("A2", "money", "Set up starter chart of accounts", False, .45),
    ("A3", "money", "Separate personal and business money", False, .40),
    ("A4", "money", "Set up receipts workflow", False, .45),
    ("A5", "money", "Put estimated-tax dates on the calendar", True, .50),
    ("A6", "money", "Adopt monthly close checklist", False, .90),
    ("O1", "ops", "Write first SOPs", False, .70),
    ("O2", "ops", "Build vendor and supplier list", False, .50),
    ("O3", "ops", "Set inventory counts and reorder points", False, .65),
    ("O4", "ops", "Write customer support macros", False, .75),
    ("O5", "ops", "Schedule the weekly founder review", False, .05),
]


def today(a):
    return date.fromisoformat(a.today) if a.today else date.today()


def path():
    return Path(os.environ.get("FOUNDER_BOARD", Path.home() / "founder-bot" / "board.json"))


def load():
    p = path()
    if not p.exists():
        sys.exit(f"no board at {p}; run: board.py init --mission NAME --launch YYYY-MM-DD")
    return json.loads(p.read_text())


def save(b):
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(b, indent=2) + "\n")
    tmp.replace(p)


def find(b, tid):
    for t in b["tasks"]:
        if t["id"].lower() == tid.lower():
            return t
    sys.exit(f"no task {tid}")


def counts(b, area=None):
    ts = [t for t in b["tasks"] if (area is None or t["area"] == area) and t["status"] != "skipped"]
    return sum(t["status"] == "done" for t in ts), len(ts)


def pct(b):
    d, n = counts(b)
    return round(100 * d / n) if n else 0


def open_tasks(b):
    return [t for t in b["tasks"] if t["status"] not in ("done", "skipped")]


def next_up(b, n):
    return sorted(open_tasks(b), key=lambda t: (t["status"] != "doing", t.get("due") or "9999", t["id"]))[:n]


def wins(b, t0):
    wk = (t0 - timedelta(days=7)).isoformat()
    return [t for t in b["tasks"] if t["status"] == "done" and (t.get("done_on") or "") > wk]


def deadlines(b, t0, within):
    out = []
    for t in sorted(open_tasks(b), key=lambda t: (t.get("due") or "9999", t["id"])):
        if t.get("due"):
            days = (date.fromisoformat(t["due"]) - t0).days
            if days <= within:
                out.append({**t, "days": days})
    return out


def line(t, t0):
    late = t.get("due") and t["status"] not in ("done", "skipped") and date.fromisoformat(t["due"]) < t0
    flag = " [needs your yes]" if t["needs_yes"] and t["status"] not in ("done", "skipped") else ""
    return f"  [{t['status']:<7}] {t['id']:<4} {t['title']} (due {t.get('due') or '-'}){' OVERDUE' if late else ''}{flag}"


def cmd_init(a):
    p = path()
    if p.exists() and not a.force:
        sys.exit(f"board exists at {p} (use --force to replace)")
    t0, launch = today(a), date.fromisoformat(a.launch)
    runway = max((launch - t0).days, 7)
    only = {x.strip() for x in a.areas.split(",")} if a.areas else None
    tasks = [{"id": i, "area": ar, "title": ti, "status": "todo", "needs_yes": ny,
              "due": (t0 + timedelta(days=round(runway * f))).isoformat(), "note": "", "source": "", "done_on": None}
             for i, ar, ti, ny, f in LIBRARY if only is None or ar in only]
    save({"mission": a.mission, "codename": a.codename or "", "launch": launch.isoformat(),
          "created": t0.isoformat(), "tasks": tasks, "history": []})
    print(f"board created at {p}: {len(tasks)} tasks, launch {launch} ({runway} days)")


def cmd_add(a):
    b = load()
    ids, n = {t["id"] for t in b["tasks"]}, 1
    while f"{PREFIX[a.area]}{n}" in ids:
        n += 1
    t = {"id": f"{PREFIX[a.area]}{n}", "area": a.area, "title": a.title, "status": "todo",
         "needs_yes": a.needs_yes, "due": a.due, "note": "", "source": a.source or "", "done_on": None}
    b["tasks"].append(t)
    save(b)
    print(f"added {t['id']}: {t['title']}")


def cmd_set(a):
    if a.status not in STATUSES:
        sys.exit(f"status must be one of {', '.join(STATUSES)}")
    b = load()
    t = find(b, a.id)
    old = t["status"]
    t["status"] = a.status
    for k in ("note", "due", "source"):
        if getattr(a, k):
            t[k] = getattr(a, k)
    t["done_on"] = today(a).isoformat() if a.status == "done" else None
    b["history"].append({"on": today(a).isoformat(), "id": t["id"], "from": old, "to": a.status})
    save(b)
    print(f"{t['id']} {old} -> {a.status}: {t['title']}")


def cmd_show(a):
    b, t0 = load(), today(a)
    d, n = counts(b)
    print(f"{b['mission']}  launch {b['launch']}  {d}/{n} done ({pct(b)}%)")
    for key, lab in AREAS:
        dd, nn = counts(b, key)
        if (a.area and a.area != key) or not nn:
            continue
        print(f"{lab} {dd}/{nn}")
        for t in (x for x in b["tasks"] if x["area"] == key):
            print(line(t, t0))


def cmd_next(a):
    b, t0 = load(), today(a)
    ts = next_up(b, a.n)
    print("\n".join(line(t, t0) for t in ts) if ts else "  all clear")


def cmd_deadlines(a):
    ds = deadlines(load(), today(a), a.within)
    if a.json:
        print(json.dumps(ds, indent=2))
        return
    for t in ds:
        when = f"{-t['days']}d overdue" if t["days"] < 0 else ("today" if t["days"] == 0 else f"in {t['days']}d")
        print(f"  {t['id']:<4} {t['title']} ({when}){' [needs your yes]' if t['needs_yes'] else ''}")
    if not ds:
        print("QUIET: nothing due")


def cmd_review(a):
    b, t0 = load(), today(a)
    d, n = counts(b)
    w, over = wins(b, t0), deadlines(b, t0, -1)
    waiting = [t for t in open_tasks(b) if t["status"] == "waiting"]
    days = (date.fromisoformat(b["launch"]) - t0).days
    j = lambda ts: "; ".join(f"{t['id']} {t['title']}" for t in ts) or "none"
    print(f"WEEK OF {t0}: {d}/{n} done ({pct(b)}%), T-{days} days to launch")
    print("Stages: " + ", ".join(f"{lab} {counts(b, k)[0]}/{counts(b, k)[1]}" for k, lab in AREAS if counts(b, k)[1]))
    print(f"Wins this week ({len(w)}): {j(w)}")
    print(f"Overdue ({len(over)}): {j(over)}")
    print(f"Waiting on you ({len(waiting)}): {j(waiting)}")
    print(f"Next 3: {j(next_up(b, 3))}")


def build_spec(b, t0, anonymous=False):
    d, n = counts(b)
    return {
        "type": "launch-board",
        "mission": (b.get("codename") or "Project Stealth") if anonymous else b["mission"],
        "launch_label": date.fromisoformat(b["launch"]).strftime("%b %d, %Y").replace(" 0", " "),
        "days_to_launch": (date.fromisoformat(b["launch"]) - t0).days,
        "stages": [{"key": k, "label": lab, "done": counts(b, k)[0], "total": counts(b, k)[1]}
                   for k, lab in AREAS if counts(b, k)[1]],
        "done": d, "total": n,
        "next": [t["title"] for t in next_up(b, 3)],
        "wins_week": len(wins(b, t0)),
        "week_label": t0.strftime("Week of %b %d").replace(" 0", " "),
        "anonymous": anonymous,
    }


def cmd_spec(a):
    out = json.dumps(build_spec(load(), today(a), a.anonymous), indent=2)
    if a.out:
        Path(a.out).write_text(out + "\n")
        print(f"wrote {a.out}")
    else:
        print(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--today")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init")
    p.add_argument("--mission", required=True); p.add_argument("--launch", required=True)
    p.add_argument("--codename"); p.add_argument("--areas"); p.add_argument("--force", action="store_true")
    p = sp.add_parser("add")
    p.add_argument("--area", required=True, choices=list(PREFIX)); p.add_argument("--title", required=True)
    p.add_argument("--due"); p.add_argument("--needs-yes", action="store_true"); p.add_argument("--source")
    p = sp.add_parser("set")
    p.add_argument("id"); p.add_argument("status"); p.add_argument("--note"); p.add_argument("--due"); p.add_argument("--source")
    sp.add_parser("show").add_argument("--area")
    sp.add_parser("next").add_argument("--n", type=int, default=5)
    p = sp.add_parser("deadlines")
    p.add_argument("--within", type=int, default=14); p.add_argument("--json", action="store_true")
    sp.add_parser("review")
    p = sp.add_parser("spec")
    p.add_argument("--anonymous", action="store_true"); p.add_argument("--out")
    a = ap.parse_args()
    globals()["cmd_" + a.cmd](a)


if __name__ == "__main__":
    main()
