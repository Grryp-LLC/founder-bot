# Samples (SAMPLE · DEMO DATA)

All four Launch Boards are fictional businesses built from demo data through the real engine and renderer. Every
card carries a red "SAMPLE · DEMO DATA" stamp.

| Board | Story | Files |
|---|---|---|
| Juniper & Ash Candle Co. | Day 5, 15%, T-68: legal fueling, store on standby | `sample-early-1200x675.png`, `sample-early-1080x1350.png` |
| Fieldnote Coffee Roasters | Mid-flight, 59%, T-25: LEGAL is GO | `sample-mid-1200x675.png`, `sample-mid-1080x1350.png` |
| Tidewater Soap Works | Launch day, 100%, T-ZERO: every stage GO, rocket clear of the tower | `sample-liftoff-1200x675.png`, `sample-liftoff-1080x1350.png` |
| Project Nightjar (stealth mode) | 97%, T-4: all systems go, brand hidden behind a codename | `sample-stealth-1200x675.png`, `sample-stealth-1080x1350.png` |

Specs are in `specs/`, and captions in `*-caption.txt` (each passes the privacy lint and is under 200 characters).
The PNGs aren't committed (the repo is text-only). Regenerate everything with `bash samples/make_samples.sh` after `./install.sh`.
