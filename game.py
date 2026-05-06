import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

MAX_LEVEL = 8
STARTING_HP = 100
STARTING_GOLD = 10
SHOP_SIZE = 5
BENCH_LIMIT = 9

LEVEL_TO_FIELD_LIMIT = {
    1: 1,
    2: 2,
    3: 2,
    4: 3,
    5: 3,
    6: 4,
    7: 4,
    8: 5,
}

XP_TO_NEXT = {
    1: 2,
    2: 4,
    3: 6,
    4: 10,
    5: 20,
    6: 32,
    7: 50,
    8: 0,
}

ROLL_ODDS = {
    1: {1: 1.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
    2: {1: 0.75, 2: 0.25, 3: 0.00, 4: 0.00, 5: 0.00},
    3: {1: 0.55, 2: 0.35, 3: 0.10, 4: 0.00, 5: 0.00},
    4: {1: 0.35, 2: 0.40, 3: 0.20, 4: 0.05, 5: 0.00},
    5: {1: 0.20, 2: 0.35, 3: 0.30, 4: 0.13, 5: 0.02},
    6: {1: 0.10, 2: 0.25, 3: 0.35, 4: 0.25, 5: 0.05},
    7: {1: 0.05, 2: 0.15, 3: 0.30, 4: 0.35, 5: 0.15},
    8: {1: 0.02, 2: 0.08, 3: 0.22, 4: 0.38, 5: 0.30},
}

BASE_DAMAGE = {
    1: {"correct": 3, "wrong": 2, "timeout": 3},
    2: {"correct": 5, "wrong": 3, "timeout": 5},
    3: {"correct": 8, "wrong": 5, "timeout": 8},
    4: {"correct": 12, "wrong": 8, "timeout": 12},
    5: {"correct": 18, "wrong": 12, "timeout": 18},
}

TIME_LIMITS = {1: 20, 2: 30, 3: 45, 4: 60, 5: 75}

SYNERGIES = {
    "electrostatics": [2, 3, 5],
    "gauss": [1, 3, 4],
    "circuits": [2, 3, 4],
    "magnetism": [2, 4, 5],
    "induction": [1, 2, 4, 5],
    "potential": [2, 3, 5],
    "differential": [1, 3, 5],
    "combined": [1, 2, 3],
}

SYNERGY_DAMAGE = {
    "electrostatics": {2: 2, 3: 4, 5: 7},
    "gauss": {1: 2, 3: 5, 4: 8},
    "circuits": {2: 2, 3: 4, 4: 6},
    "magnetism": {2: 2, 4: 5, 5: 7},
    "induction": {1: 1, 2: 3},
    "potential": {2: 2, 3: 4},
    "differential": {1: 2, 3: 5},
    "combined": {1: 3, 2: 6, 3: 10},
}


@dataclass
class ProblemUnit:
    name: str
    cost: int
    tags: List[str]
    star: int = 1

    def damage_multiplier(self) -> float:
        return {1: 1.0, 2: 1.5, 3: 2.0}[self.star]


PROBLEM_POOL = [
    ProblemUnit("Field Direction", 1, ["electrostatics"]),
    ProblemUnit("Formula Match", 1, ["electrostatics", "potential"]),
    ProblemUnit("Unit Check", 1, ["circuits"]),
    ProblemUnit("Point Charge E", 2, ["electrostatics"]),
    ProblemUnit("Parallel Plate C", 2, ["circuits"]),
    ProblemUnit("Ohm Quick", 2, ["circuits"]),
    ProblemUnit("Lorentz Force", 2, ["magnetism"]),
    ProblemUnit("Gauss Shell", 3, ["gauss", "electrostatics"]),
    ProblemUnit("RC Initial", 3, ["circuits", "differential"]),
    ProblemUnit("Flux Basic", 3, ["induction", "magnetism"]),
    ProblemUnit("Potential + Field", 4, ["potential", "electrostatics", "combined"]),
    ProblemUnit("Capacitance + Energy", 4, ["circuits", "combined"]),
    ProblemUnit("Force + Circular", 4, ["magnetism", "combined"]),
    ProblemUnit("Faraday Final", 5, ["induction", "magnetism", "combined"]),
    ProblemUnit("Potential Integral", 5, ["potential", "gauss", "combined"]),
    ProblemUnit("Transient Master", 5, ["differential", "circuits", "combined"]),
]


@dataclass
class Player:
    name: str
    hp: int = STARTING_HP
    gold: int = STARTING_GOLD
    level: int = 1
    xp: int = 0
    bench: List[ProblemUnit] = field(default_factory=list)
    fielded: List[ProblemUnit] = field(default_factory=list)
    streak: int = 0

    def field_limit(self) -> int:
        return LEVEL_TO_FIELD_LIMIT[self.level]

    def add_xp(self, amount: int) -> None:
        if self.level >= MAX_LEVEL:
            return
        self.xp += amount
        while self.level < MAX_LEVEL and self.xp >= XP_TO_NEXT[self.level]:
            self.xp -= XP_TO_NEXT[self.level]
            self.level += 1


class Game:
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.players = [Player("Player 1"), Player("Player 2")]
        self.round = 1

    def weighted_cost(self, level: int) -> int:
        roll = self.rng.random()
        acc = 0.0
        for cost, p in ROLL_ODDS[level].items():
            acc += p
            if roll <= acc:
                return cost
        return 1

    def roll_shop(self, player: Player) -> List[ProblemUnit]:
        shop = []
        for _ in range(SHOP_SIZE):
            cost = self.weighted_cost(player.level)
            choices = [u for u in PROBLEM_POOL if u.cost == cost]
            picked = self.rng.choice(choices)
            shop.append(ProblemUnit(picked.name, picked.cost, list(picked.tags)))
        return shop

    def buy_best(self, player: Player, shop: List[ProblemUnit]) -> None:
        affordable = [u for u in shop if u.cost <= player.gold]
        affordable.sort(key=lambda u: (u.cost, len(u.tags)), reverse=True)
        for unit in affordable:
            if len(player.bench) >= BENCH_LIMIT:
                break
            if unit.cost <= player.gold:
                player.gold -= unit.cost
                player.bench.append(unit)
        self.merge_stars(player)

    def merge_stars(self, player: Player) -> None:
        changed = True
        while changed:
            changed = False
            counter: Dict[tuple, List[int]] = {}
            for i, unit in enumerate(player.bench):
                key = (unit.name, unit.star)
                counter.setdefault(key, []).append(i)
            for (name, star), idxs in list(counter.items()):
                if len(idxs) >= 3 and star < 3:
                    keep = idxs[0]
                    remove = sorted(idxs[1:3], reverse=True)
                    player.bench[keep].star += 1
                    for ridx in remove:
                        del player.bench[ridx]
                    changed = True
                    break

    def set_field(self, player: Player) -> None:
        units = sorted(player.bench, key=lambda u: (u.star, u.cost, len(u.tags)), reverse=True)
        player.fielded = units[: player.field_limit()]

    def active_synergy_counts(self, player: Player) -> Dict[str, int]:
        counts = {k: 0 for k in SYNERGIES}
        for u in player.fielded:
            for t in u.tags:
                if t in counts:
                    counts[t] += 1
        return counts

    def synergy_tier(self, syn: str, count: int) -> int:
        active = 0
        for need in SYNERGIES[syn]:
            if count >= need:
                active = need
        return active

    def calc_damage(self, attacker: Player, defender: Player) -> int:
        total = 0
        syn_count = self.active_synergy_counts(attacker)
        circuit_correct = 0
        for u in attacker.fielded:
            result = self.rng.choices(["correct", "wrong", "timeout"], weights=[0.68, 0.22, 0.10])[0]
            base = BASE_DAMAGE[u.cost]
            if result == "correct":
                dmg = int(base["correct"] * u.damage_multiplier())
                for tag in u.tags:
                    tier = self.synergy_tier(tag, syn_count.get(tag, 0))
                    dmg += SYNERGY_DAMAGE.get(tag, {}).get(tier, 0)
                    if tag == "magnetism" and tier == 5 and self.rng.random() < 0.3:
                        dmg *= 2
                    if tag == "induction" and tier == 4:
                        dmg += 3
                    if tag == "induction" and tier == 5:
                        dmg += int(dmg * 0.4)
                if "differential" in u.tags and self.synergy_tier("differential", syn_count["differential"]) == 5:
                    defender.hp -= 6
                if "electrostatics" in u.tags and self.synergy_tier("electrostatics", syn_count["electrostatics"]) == 5:
                    defender.hp -= 0
                total += dmg
                if "circuits" in u.tags:
                    circuit_correct += 1
            else:
                attacker.hp -= base[result]
                if result == "wrong" and self.synergy_tier("electrostatics", syn_count["electrostatics"]) == 5:
                    defender.hp -= 2
        if self.synergy_tier("circuits", syn_count["circuits"]) == 4 and circuit_correct >= 2:
            total += 3
        return max(0, total)

    def settlement(self, winner: Optional[Player], loser: Optional[Player]) -> None:
        if winner and loser:
            winner.streak = max(1, winner.streak + 1)
            loser.streak = min(-1, loser.streak - 1)
        for p in self.players:
            p.gold += 5
            streak = abs(p.streak)
            if streak >= 5:
                p.gold += 3
            elif streak >= 3:
                p.gold += 2
            elif streak >= 2:
                p.gold += 1
            p.add_xp(2)

    def play_round(self) -> None:
        for p in self.players:
            shop = self.roll_shop(p)
            self.buy_best(p, shop)
            self.set_field(p)
        d1 = self.calc_damage(self.players[0], self.players[1])
        d2 = self.calc_damage(self.players[1], self.players[0])
        self.players[1].hp -= d1
        self.players[0].hp -= d2

        winner = loser = None
        if d1 > d2:
            winner, loser = self.players[0], self.players[1]
        elif d2 > d1:
            winner, loser = self.players[1], self.players[0]
        self.settlement(winner, loser)
        self.round += 1

    def done(self) -> bool:
        alive = [p for p in self.players if p.hp > 0]
        return len(alive) <= 1

    def winner(self) -> Optional[Player]:
        alive = [p for p in self.players if p.hp > 0]
        return alive[0] if len(alive) == 1 else None


def print_state(game: Game) -> None:
    print(f"\n=== Round {game.round} ===")
    for p in game.players:
        print(
            f"{p.name}: HP={p.hp} Gold={p.gold} Level={p.level} XP={p.xp}/{XP_TO_NEXT[p.level] if p.level < MAX_LEVEL else 'MAX'} "
            f"Field={[(u.name, u.cost, u.star) for u in p.fielded]}"
        )


def main() -> None:
    game = Game(seed=42)
    print("AP Physics C: E&M Auto-Chess Quiz Game (Simulation)")
    print("Quick mode: automated shop + quiz outcomes with full rule tables encoded.")
    while not game.done() and game.round <= 30:
        game.play_round()
        print_state(game)
    w = game.winner()
    if w:
        print(f"\nWinner: {w.name} with {w.hp} HP remaining")
    else:
        print("\nNo single winner within 30 rounds.")


if __name__ == "__main__":
    main()
