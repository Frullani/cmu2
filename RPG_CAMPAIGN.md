# RPG Campaign

This project uses the [claude-rpg-skill](.claude/skills/rpg/README.md) for long-form
roleplay narration with persistent canon, a finance ledger, and anti-drift discipline.

memory_dir: rpg-campaign/memory

## How to use

- In a Claude Code chat, type `/rpg` to boot the campaign (the SessionStart hook also
  auto-loads canon every session).
- Canon lives under `rpg-campaign/memory/` — one markdown file per NPC / location /
  ship / contract, plus structured JSON state and an economy ledger.
- See `.claude/skills/rpg/SKILL.md` for the full command list and disciplines.
