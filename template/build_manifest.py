#!/usr/bin/env python3
"""Rebuild template/template-manifest.json from bot-profile.md, skills/, routines/, memories/."""
import json, re
from pathlib import Path
R = Path(__file__).resolve().parent.parent
strip = lambda t: re.sub(r'^---.*?---\n', '', t, flags=re.S).strip()
prof = (R / "bot-profile.md").read_text()
system_prompt = re.search(r"## System prompt / persona\n\n```\n(.*?)\n```", prof, re.S).group(1)
short = re.search(r"\*\*Short description\*\*[^|]*\|\s*(.*?)\s*\|\n", prof).group(1)
SKILLS = ["founder-bot-getting-started", "launch-plan", "incorporate", "ecommerce-setup", "marketing-launch",
          "accounting-setup", "operations-setup", "weekly-founder-review"]
skills = []
for d in SKILLS:
    t = (R / "skills" / d / "SKILL.md").read_text()
    desc = " ".join(re.search(r"description: >-\n(.*?)\n---", t, re.S).group(1).split())
    skills.append({"name": d, "description": desc, "job": strip(t)})
rt = (R / "routines" / "ROUTINES.md").read_text()
routines = []
for name, cron in [("weekly-founder-review", "30 8 * * 1"), ("deadline-reminders", "0 8 * * *")]:
    m = re.search(r"## \d\. " + name + r".*?\*\*Prompt:\*\*\n(.*?)(?=\n## |\Z)", rt, re.S)
    routines.append({"name": name, "schedule": cron, "timezone": "owner local",
                     "prompt": " ".join(l.strip().lstrip(">").strip() for l in m.group(1).splitlines() if l.strip())})
mem = [" ".join(x.split()) for x in re.split(r"\n- ", "\n" + (R / "memories" / "profile.md").read_text()) if x.strip()]
manifest = {
    "audience": "public",
    "name": "Founder Bot",
    "title": "Your co-founder on day one",
    "avatar": {"shape": "hex", "color": "orange"},
    "description": short,
    "systemPrompt": system_prompt,
    "memories": {"profile": mem, "log": [" ".join((R / "memories" / "log.md").read_text().lstrip("- ").split())]},
    "skills": skills,
    "routines": routines,
    "routinesNote": "Created by founder-bot-getting-started in the new owner's timezone; specs in routines/ROUTINES.md.",
    "plugins": [
        "Gmail (core; marketplace connector, if available; read and search, Gmail drafts only with a yes, never sends)",
        "Google Drive (core; marketplace connector, if available; docs only in the owner's 'Founder Bot' folder after a yes)",
        "Google Calendar (core; marketplace connector, if available; read, and add deadline events with a yes)",
        "Shopify (optional; marketplace connector, if available; read, and create draft products with a yes; never publishes)",
        "Stripe (optional; marketplace connector, if available; read-only account checks)",
    ],
    "gettingStarted": "founder-bot-getting-started",
}
(R / "template" / "template-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
print("wrote", R / "template" / "template-manifest.json", len(json.dumps(manifest)), "bytes")
