# Routines

Both routines are cron schedules in the owner's local timezone, created by `founder-bot-getting-started`. Prompts are
written as intents. Look up connector tools with MCP discovery at run time, and don't hard-code tool schemas. Quiet
rule: **a run with nothing to say sends no message.** Neither routine ever spends, files, submits, sends, or posts
anything.

## 1. weekly-founder-review
- **Schedule:** `30 8 * * 1` (Mondays 8:30 AM owner-local, adjustable)
- **Prompt:**
  > Run the weekly-founder-review skill. Read the Launch Board, check deadlines for the next 14 days, and (read-only,
  > if connected) check Calendar and Gmail for official notices about filings, approvals, or deadlines. Send the owner
  > one message of at most 12 lines: T-minus and % complete, wins, overdue or due within 7 days (with next action and
  > whether it needs their yes), what's waiting on them, and this week's 3 priorities. If posters are on, render the
  > Launch Board card at 1200x675 and 1080x1350 through the privacy gate and attach it with a caption under 200
  > characters. Never send email, file, pay, publish, or post anything. If the board hasn't changed in 14 days and
  > nothing is due, send a 2-line nudge with the single next action instead.

## 2. deadline-reminders
- **Schedule:** `0 8 * * *` (daily 8:00 AM owner-local, adjustable)
- **Prompt:**
  > Run `board.py deadlines --within 3 --json`. If nothing is due within 3 days and nothing is overdue, send no message.
  > Otherwise send at most 5 short lines: task, due date, what to do, time it takes, and "needs your yes" where
  > relevant. Include tax, annual report, and sales tax filing dates that are on the board (they were looked up and
  > cited when added. If a source is missing, say to confirm the date on the official site). Remind about the same task
  > at most once a day, and stop after the owner says done, skip, or snooze. Never file, pay, or send anything.

## Owner controls
"go quiet" pauses both, "wake up" resumes them, "move my review to Friday 4pm" edits weekly-founder-review, and
"remind me 7 days ahead" changes `--within` for deadline-reminders.
