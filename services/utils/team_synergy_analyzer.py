from collections import defaultdict
from typing import Dict, List, Set, Tuple

from django.db.models import Prefetch

from pokedex.models import Pokemon, PokemonType

from .type_effectiveness import TypeEffectivenessService


class TeamAnalysisService:
    """Service for analyzing Pokémon team synergy."""

    @staticmethod
    def analyze_team_synergy(team_pokemon: List[Pokemon]) -> Dict:
        """
        Analyze a team of Pokémon with a focus on team-level matchups.

        Args:
            team_pokemon: List of Pokémon objects to analyze

        Returns:
            Dictionary containing synergy analysis results
        """

        # Handle empty team case
        if not team_pokemon:
            return {
                "score": 0,
                "major_threats": [],
                "balanced_matchups": [],
                "safe_matchups": [],
                "suggestions": [],
            }

        # Prefetch types to avoid N+1 queries
        team_with_types = Pokemon.objects.filter(
            id__in=[p.id for p in team_pokemon]
        ).prefetch_related("types")

        # Get all type names
        all_type_names = TypeEffectivenessService.get_all_type_names()

        # Analyze each type against the team
        type_analysis = {}
        for attacking_type in all_type_names:
            analysis = TeamAnalysisService._analyze_type_matchup(
                attacking_type, team_with_types
            )
            type_analysis[attacking_type] = analysis

        # Categorize matchups
        major_threats, balanced_matchups, safe_matchups = (
            TeamAnalysisService._categorize_matchups(type_analysis)
        )

        # Analyze offensive coverage
        offensive_strengths = TeamAnalysisService._analyze_offensive_coverage(
            team_with_types, all_type_names
        )

        # Calculate synergy score
        score = TeamAnalysisService._calculate_synergy_score(
            major_threats, balanced_matchups, safe_matchups
        )

        # Generate suggestions
        suggestions = TeamAnalysisService._generate_suggestions(
            major_threats, balanced_matchups, safe_matchups, offensive_strengths
        )

        return {
            "score": score,
            "major_threats": major_threats,
            "balanced_matchups": balanced_matchups,
            "safe_matchups": safe_matchups,
            "suggestions": suggestions,
        }

    @staticmethod
    def _analyze_type_matchup(attacking_type: str, team_pokemon: List[Pokemon]) -> Dict:
        """Analyze how a specific type affects the team."""
        weak_count = 0
        resist_count = 0
        immune_count = 0
        vulnerable_pokemon = []
        resistant_pokemon = []
        immune_pokemon = []
        worst_multiplier = 1.0

        for pokemon in team_pokemon:
            # Get the Pokémon's types
            pokemon_types = [t.name for t in pokemon.types.all()]

            # Calculate effectiveness
            effectiveness = TypeEffectivenessService.calculate_effectiveness(
                attacking_type, pokemon_types
            )

            # Track counts
            if effectiveness > 1:
                weak_count += 1
                vulnerable_pokemon.append(
                    {"name": pokemon.name, "effectiveness": effectiveness}
                )
                if effectiveness > worst_multiplier:
                    worst_multiplier = effectiveness
            elif effectiveness < 1 and effectiveness > 0:
                resist_count += 1
                resistant_pokemon.append(
                    {"name": pokemon.name, "effectiveness": effectiveness}
                )
            elif effectiveness == 0:
                immune_count += 1
                immune_pokemon.append(
                    {"name": pokemon.name, "effectiveness": effectiveness}
                )

        return {
            "weak_count": weak_count,
            "resist_count": resist_count,
            "immune_count": immune_count,
            "vulnerable_pokemon": vulnerable_pokemon,
            "resistant_pokemon": resistant_pokemon,
            "immune_pokemon": immune_pokemon,
            "worst_multiplier": worst_multiplier,
        }

    @staticmethod
    def _categorize_matchups(type_analysis: Dict) -> Tuple[List, List, List]:
        """Categorize type matchups into major threats, balanced, and safe."""
        major_threats = []
        balanced_matchups = []
        safe_matchups = []

        for type_name, analysis in type_analysis.items():
            # Major threat: multiple weaknesses and no resistances/immunities
            if (
                analysis["weak_count"] >= 2
                and analysis["resist_count"] == 0
                and analysis["immune_count"] == 0
            ):
                major_threats.append(
                    {
                        "type": type_name,
                        "weak_count": analysis["weak_count"],
                        "worst_multiplier": analysis["worst_multiplier"],
                        "vulnerable_pokemon": analysis["vulnerable_pokemon"],
                    }
                )
            # Balanced: both weaknesses and resistances/immunities
            elif analysis["weak_count"] > 0 and (
                analysis["resist_count"] > 0 or analysis["immune_count"] > 0
            ):
                balanced_matchups.append(
                    {
                        "type": type_name,
                        "weak_count": analysis["weak_count"],
                        "resist_count": analysis["resist_count"],
                        "immune_count": analysis["immune_count"],
                        "vulnerable_pokemon": analysis["vulnerable_pokemon"],
                        "resistant_pokemon": analysis["resistant_pokemon"],
                        "immune_pokemon": analysis["immune_pokemon"],
                    }
                )
            # Safe: no weaknesses and at least one resistance/immunity
            elif analysis["weak_count"] == 0 and (
                analysis["resist_count"] > 0 or analysis["immune_count"] > 0
            ):
                safe_matchups.append(
                    {
                        "type": type_name,
                        "resist_count": analysis["resist_count"],
                        "immune_count": analysis["immune_count"],
                        "resistant_pokemon": analysis["resistant_pokemon"],
                        "immune_pokemon": analysis["immune_pokemon"],
                    }
                )

        return major_threats, balanced_matchups, safe_matchups

    @staticmethod
    def _analyze_offensive_coverage(
        team_pokemon: List[Pokemon], all_type_names: Set[str]
    ) -> List[Dict]:
        """Analyze which types the team can hit super effectively."""
        offensive_coverage = defaultdict(list)

        for defending_type in all_type_names:
            for pokemon in team_pokemon:
                # Get the Pokémon's types
                pokemon_types = [t.name for t in pokemon.types.all()]

                # Check if any of the Pokémon's types are super effective against the defending type
                for pokemon_type in pokemon_types:
                    effectiveness = TypeEffectivenessService.calculate_effectiveness(
                        pokemon_type, [defending_type]
                    )
                    if effectiveness > 1:
                        offensive_coverage[defending_type].append(
                            {
                                "pokemon": pokemon.name,
                                "type": pokemon_type,
                                "effectiveness": effectiveness,
                            }
                        )

        # Format for response
        strengths = []
        for type_name, coverage in offensive_coverage.items():
            if coverage:
                best_effectiveness = max([c["effectiveness"] for c in coverage])
                strengths.append(
                    {
                        "type": type_name,
                        "best_effectiveness": best_effectiveness,
                        "coverage": coverage,
                    }
                )

        return strengths

    @staticmethod
    def _calculate_synergy_score(
        major_threats: List, balanced_matchups: List, safe_matchups: List
    ) -> int:
        """Calculate a synergy score between 0-100 based on team strengths and weaknesses."""
        # Start with a base score
        score = 70

        # Penalize for major threats
        for threat in major_threats:
            penalty = threat["weak_count"] * 5 + (threat["worst_multiplier"] - 1) * 10
            score -= penalty

        # Reward for safe matchups
        for safe in safe_matchups:
            reward = (safe["resist_count"] + safe["immune_count"]) * 3
            score += reward

        # Ensure score is between 0 and 100
        return max(0, min(100, score))

    @staticmethod
    def _generate_suggestions(
        major_threats: List,
        balanced_matchups: List,
        safe_matchups: List,
        offensive_strengths: List,
    ) -> List[str]:
        """Generate targeted suggestions to improve team synergy."""
        suggestions = []

        # Suggestions for major threats
        for threat in major_threats:
            # Find types that resist this threat
            resisting_types = TeamAnalysisService._find_types_that_resist(
                threat["type"]
            )

            if resisting_types:
                suggestions.append(
                    f"Major threat: {threat['type'].capitalize()} - {threat['weak_count']} Pokémon weak, "
                    f"no reliable counters. Consider adding {', '.join(resisting_types)} type Pokémon."
                )

        # Highlight stacking weaknesses
        stacking_threats = [t for t in major_threats if t["weak_count"] >= 3]
        for threat in stacking_threats:
            suggestions.append(
                f"Stacking weakness: {threat['type'].capitalize()} - {threat['weak_count']} Pokémon are weak. "
                f"This is a critical vulnerability."
            )

        # Highlight safe matchups
        strong_defenses = [
            s for s in safe_matchups if s["resist_count"] + s["immune_count"] >= 3
        ]
        for defense in strong_defenses:
            suggestions.append(
                f"Strong defense: Your team handles {defense['type'].capitalize()} well with "
                f"{defense['resist_count'] + defense['immune_count']} resistances/immunities."
            )

        # Highlight offensive coverage gaps
        all_type_names = TypeEffectivenessService.get_all_type_names()
        covered_types = set(
            [s["type"] for s in offensive_strengths if s["best_effectiveness"] >= 2]
        )
        uncovered_types = all_type_names - covered_types

        if uncovered_types:
            suggestions.append(
                f"Offensive gap: Your team can't hit {', '.join(uncovered_types)} types super effectively. "
                f"Consider adding Pokémon with types that cover these weaknesses."
            )

        # If no major issues, provide positive feedback
        if not suggestions:
            suggestions.append("Your team has excellent type coverage and synergy!")

        return suggestions

    @staticmethod
    def _find_types_that_resist(attacking_type: str) -> List[str]:
        """Find types that resist a given attacking type."""
        resisting_types = []
        all_type_names = TypeEffectivenessService.get_all_type_names()

        for defending_type in all_type_names:
            effectiveness = TypeEffectivenessService.calculate_effectiveness(
                attacking_type, [defending_type]
            )

            if effectiveness < 1:
                resisting_types.append(defending_type)

        return resisting_types
