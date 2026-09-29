# Publishing notes (Grok Bot template)

1. Create the bot: name `Founder Bot`, title `Your co-founder on day one`, avatar hex/orange, description and system
   prompt from `bot-profile.md`.
2. Add the eight skills from `skills/*/SKILL.md`. `founder-bot-getting-started` must be one of the bot's real skills
   so it gets packed.
3. Add the memories from `memories/profile.md` (one entry per bullet) and `memories/log.md`.
4. The kit install URL is pinned in `memories/profile.md` (`launch_kit_url`) to commit `7b37f63` of
   github.com/Grryp-LLC/founder-bot. If the kit ever changes, re-pin and re-run `python3 template/build_manifest.py`.
5. Routines are created by `founder-bot-getting-started` in each new owner's timezone. Specs are in
   `routines/ROUTINES.md`.
6. Plugins, each connected only if available: core set Gmail, Google Drive, Google Calendar, plus optional Shopify
   and Stripe (marketplace connectors). No custom MCP servers.
7. Pack with gettingStarted = `founder-bot-getting-started`, using `template/template-manifest.json` as the source.

Never included: real owner or business data, personal names, emails, tax IDs, account numbers, tokens. Sample
businesses are fictional.
