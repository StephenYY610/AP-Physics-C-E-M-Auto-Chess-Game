# AP Physics C: E&M Auto-Chess Quiz Game (Web)

This is now an **actual browser game** (not a passive simulation).

## Features implemented
- Two-player local play on one device.
- Shop phase with reroll, buy, sell, buy-XP, bench, auto-set-field.
- Level/XP progression and field size limits.
- Unit costs 1–5 with star upgrades (3 copies merge).
- Quiz battle phase where players answer multiple-choice prompts (A/B/C/D) for each fielded unit.
- Correct / wrong / timeout outcomes with damage and self-damage.
- Synergy bonuses (electrostatics, gauss, circuits, magnetism, induction, potential, differential, combined).
- End-of-round settlement with base income and auto XP.

## Run locally
Just open `index.html` in a browser.

For a local server:

```bash
python3 -m http.server 8000
```
Then visit `http://localhost:8000`.

## Tech
- Vanilla HTML/CSS/JavaScript (no backend required).
