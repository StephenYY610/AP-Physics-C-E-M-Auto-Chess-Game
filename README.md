# AP Physics C: E&M Auto-Chess Quiz Game

A terminal simulation of the rule set you provided:

- 1v1 auto-chess economy loop (gold, reroll, level, XP, streaks)
- AP Physics C: E&M problem units by cost (1–5)
- Star upgrades (1⭐/2⭐/3⭐)
- Synergy activation and bonus damage logic
- Round loop with shop, lineup, quiz battle, and settlement

## Run

```bash
python3 game.py
```

## Notes

- This is a **fast classroom simulation mode** (Quick Question Mode style).
- Question-answering is simulated probabilistically per unit (`correct/wrong/timeout`) so rounds resolve quickly.
- The encoded constants map directly to your rules (XP table, field limits, reroll odds, base damage, synergy thresholds).
