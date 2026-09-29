---
name: launch-plan
description: >-
  Build and maintain the tracked launch plan on the Launch Board (board.py), tailor tasks to the intake answers, gate
  actions that need the owner's yes, and render the shareable mission-control Launch Board card.
---
# Launch plan and Launch Board

Board file: `~/founder-bot/board.json`. Engine: `python ~/founder-bot/engine/board.py` (use the kit venv).

## Build
`board.py init --mission "<brand or working name>" --launch YYYY-MM-DD [--codename "Project X"]` seeds 34 tasks across
LEGAL (L), STORE (S), MARKETING (M), MONEY (A), OPS (O), with due dates spread over the runway. Then tailor:
- Already done in intake: `board.py set L3 done`.
- Not relevant: `skip` (no store needed for a service business: skip S5/O3; Etsy-only can skip the domain in M2
  but keep handles; sole prop by choice: skip L3/L5/L6 and add "Register DBA if using a trade name").
- Add what the business needs: `board.py add --area legal --title "Cottage food permit check" --needs-yes --source URL`.
  Regulated products (food, cosmetics, candles with claims, supplements, kids' items) always get a compliance task.
- Co-founders: operating agreement is multi-member, and add "Agree equity split and vesting (with an attorney)".

## Keep it current
- Statuses: todo, doing, waiting (on the owner: a yes, signature, or filing), done, skipped.
- `needs_yes` tasks: prepare everything, then ask a direct yes/no that says exactly what happens, what it costs (cited),
  and that they submit it. Record the answer in `--note`.
- Every fee or rule you used goes in `--source` with the official link.
- `show`, `next --n 3`, `deadlines --within 14`, `review` for summaries. If the launch date moves, re-date open tasks.

## The Launch Board card (shareable)
1. `board.py spec --out /tmp/board.json` (add `--anonymous` for stealth mode, which shows the codename).
2. Render: `python ~/founder-bot/board/render.py /tmp/board.json --out ~/founder-bot/cards --deny "<deny-list>"`
   gives `*-1200x675.png` (X landscape) and `*-1080x1350.png` (portrait). The privacy gate refuses to render if it sees
   dollar amounts, tax IDs, emails, URLs, phones, addresses, 4+ digit numbers, or deny-listed names. Fix the spec. Don't
   bypass it.
3. Send both PNGs and a caption of at most 200 characters, like "T-minus 25 days. Legal is GO, store is burning. 59% to
   launch. #buildinpublic". No links or amounts. You never post it.
4. No kit? Send the text board: a line per stage with ▓/░ bars, the % and T-minus, and the next 3 burns.
