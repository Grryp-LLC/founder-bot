# 🚀 Founder Bot: your co-founder on day one

> A Grok Bot template that interviews you about your idea, then sets up the business with you step by step (LLC,
> store, marketing, books, operations) on a tracked **Launch Board**, and hands you a mission-control progress card
> every week to post on X.

*The sample cards are fictional demo data with a red "SAMPLE · DEMO DATA" stamp. See [`samples/`](samples/README.md).*

## The pitch
Most people with a good idea stall on the boring part: which entity, which forms, what fees, which platform, what to
post, how to keep books. Founder Bot is the co-founder who has done it before. It asks one question at a time,
builds a 34-item launch plan tailored to you, drafts the documents, looks up every fee live with a citation, and walks
you through each action. **You** click submit. It never spends, files, or sends anything without your yes.

## What it does
1. **Intake interview**, one question at a time: idea, what you sell, state or country, solo or co-founders, budget,
   timeline, risk tolerance, existing assets (domain, handles), and the tools you use.
2. **A tracked launch plan** across five stages, with due dates spread over your runway:
   - **LEGAL**: entity choice (LLC vs. S-corp election vs. C-corp, with trade-offs), state filing steps and fees looked
     up live from the official registry and cited, EIN (free, straight from irs.gov), registered agent, an operating
     agreement draft, bank account, licenses and permits, sales tax, and a USPTO trademark knockout search.
   - **STORE**: Shopify / Etsy / Square / Stripe pick with cited fees, setup checklist, listing template, payments,
     shipping, and return, privacy, and terms drafts.
   - **MARKETING**: positioning worksheet, domain and handle check, launch-day T-minus plan, 30 days of posts, email
     list setup, and a small ad test plan.
   - **MONEY**: bookkeeping tool pick, starter chart of accounts, separating personal and business, a quarterly
     estimated-tax calendar (dates pulled from the IRS for the current year), receipts workflow, and a monthly close
     checklist.
   - **OPS**: SOP templates, vendor list, inventory reorder points, support macros, and the weekly founder review.
3. **Routines:** a Monday founder review (wins, deadlines, 3 priorities, a fresh card) and daily deadline reminders that
   stay silent unless something is due.
4. **The Launch Board card:** a rocket-launch mission-control PNG at 1200×675 and 1080×1350. Stages light up
   STANDBY → BURN → GO, the rocket climbs with your progress, and a T-minus countdown runs to launch day. Stealth mode
   hides your brand behind a codename. On launch day the countdown flips to **LIFTOFF**.

## Why it's fun (and safe)
- Launching a business feels like a pile of forms. Here it's a countdown, and every checked box moves the rocket.
- **Guardrails in the persona, every skill, and the routines:** no spending, filing, signing, publishing, posting, or
  sending without an explicit yes for that exact action. Government filings, bank accounts, and payments are always
  done by the owner.
- **No invented facts:** fees, deadlines, and rules are looked up live on official sources (state registry, IRS, SBA,
  USPTO, FTC, platform pricing pages) and cited with the date checked. If it can't confirm a number, it says so.
- **"Not legal or tax advice"** on every legal or tax recommendation and draft, plus a nudge to a pro where it matters.
- **Privacy gate in code:** the renderer refuses to draw dollar amounts, tax IDs, emails, URLs, phones, addresses, long
  numbers, or deny-listed names (`board/privacy.py`, tested).

## 30-second demo script
| Time | On screen | Voiceover |
|---|---|---|
| 0–5s | Blank chat, type "I want to start a candle business" | "Got an idea? Meet your co-founder on day one." |
| 5–12s | Founder Bot asks one question at a time (state, solo, budget, launch date), with quick replies | "Founder Bot interviews you, one question at a time." |
| 12–18s | The plan appears: 5 stages and the first 3 actions. "LLC in your state: filing fee [cited link], checked today" | "Then it builds your launch plan, with every fee looked up and cited, never guessed." |
| 18–24s | "draft my return policy" → a draft with a "not legal advice" footer; "file my LLC" → "Here are the steps. You submit it." | "It drafts and guides. You press submit." |
| 24–30s | The Launch Board card slides in: T-MINUS 25, rocket climbing, LEGAL GO | "And every Monday you get a launch board worth posting. Founder Bot: T-minus your business." |

## Install the kit (what the bot runs; works on any Linux/macOS box)
```bash
KIT=https://codeload.github.com/Grryp-LLC/founder-bot/tar.gz/7b37f63c85bb3c1b3302baa2965c27191be9ee9d
mkdir -p ~/founder-bot && curl -fsSL "$KIT" | tar xz --strip-components=1 -C ~/founder-bot && bash ~/founder-bot/install.sh
```
`install.sh` fetches the fonts from google/fonts at a pinned commit (SHA-256 checked), creates a venv with Playwright
and Pillow, uses system Chrome/Chromium (or installs Playwright Chromium), and runs the self-test. It's safe to re-run,
and it never touches `board.json`.

The URL is pinned to commit `7b37f63` (the last kit commit). The engine and renderer at that commit never change, so the
bot always installs exactly what was reviewed. The PNG samples aren't committed; `bash samples/make_samples.sh`
rebuilds all four.

```bash
cd ~/founder-bot
.venv/bin/python engine/board.py init --mission "My Shop" --launch 2026-12-01
.venv/bin/python engine/board.py set L1 done && .venv/bin/python engine/board.py review
.venv/bin/python engine/board.py spec --out /tmp/b.json && .venv/bin/python board/render.py /tmp/b.json --out cards
bash tests/run_tests.sh
```

## Repo layout
```
bot-profile.md            name, title, description, full system prompt
skills/<name>/SKILL.md    founder-bot-getting-started, launch-plan, incorporate, ecommerce-setup,
                          marketing-launch, accounting-setup, operations-setup, weekly-founder-review
routines/ROUTINES.md      weekly-founder-review + deadline-reminders: cron, prompt
memories/                 portable memories (profile + service log)
engine/board.py           launch board: 34-task library, statuses, deadlines, weekly review, card spec
board/render.py           HTML/CSS -> PNG (Playwright + headless Chrome), 1200x675 + 1080x1350
board/privacy.py          privacy gate (refuses to render leaks)
board/fonts/              font lock (pinned URLs + SHA-256) and OFL license; install.sh fetches the files
samples/                  SAMPLE specs, captions, make_samples.sh (PNGs are rebuilt locally)
tests/run_tests.sh        engine, quiet rule, privacy gate, renders at both sizes
template/                 Grok Bot template manifest, builder, publishing notes
install.sh                one-shot installer
```

## Licenses
Code: MIT (`LICENSE`). Fonts: Orbitron, Space Grotesk, and JetBrains Mono under SIL OFL 1.1. Sample businesses
(Juniper & Ash Candle Co., Fieldnote Coffee Roasters, Tidewater Soap Works, Project Nightjar) are fictional.
