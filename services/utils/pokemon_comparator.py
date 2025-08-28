from pokedex.models import PokemonStats


class PokemonComparator:
    STAT_FIELDS = [
        "hp",
        "attack",
        "defense",
        "special_attack",
        "special_defense",
        "speed",
    ]

    def __init__(self, pokemon1, pokemon2):
        self.p1 = pokemon1
        self.p2 = pokemon2
        self.s1: PokemonStats = pokemon1.stats
        self.s2: PokemonStats = pokemon2.stats

    def compare_stats(self):
        """Compare each stat and return per-stat winners."""
        comparison = {}
        for field in self.STAT_FIELDS:
            val1, val2 = getattr(self.s1, field), getattr(self.s2, field)
            winner = (
                self.p1.name if val1 > val2 else self.p2.name if val2 > val1 else "tie"
            )
            comparison[field] = {
                self.p1.name: val1,
                self.p2.name: val2,
                "winner": winner,
            }
        return comparison

    def total_comparison(self):
        """Compare total stats."""
        total1, total2 = self.s1.total, self.s2.total
        winner = (
            self.p1.name
            if total1 > total2
            else self.p2.name if total2 > total1 else "tie"
        )
        return {self.p1.name: total1, self.p2.name: total2, "winner": winner}

    def classify_role(self, stats: PokemonStats) -> str:
        """Assign a role based on stat profile."""
        offense = (stats.attack + stats.special_attack) / 2
        defense = (stats.defense + stats.special_defense) / 2
        tank = stats.hp

        if offense > defense and offense > tank:
            return "Offensive"
        elif defense > offense and defense > tank:
            return "Defensive"
        elif tank > offense and tank > defense:
            return "Tank"
        return "Balanced"

    def roles(self):
        return {
            self.p1.name: self.classify_role(self.s1),
            self.p2.name: self.classify_role(self.s2),
        }

    def run(self):
        """Return the full structured comparison result."""
        comparison = self.compare_stats()
        total = self.total_comparison()
        return {
            "comparison": comparison,
            "total": total,
            "roles": self.roles(),
            "overall_winner": total["winner"],
        }
