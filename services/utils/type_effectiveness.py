from typing import Dict, List, Set

from pokedex.models import PokemonType


class TypeEffectivenessService:
    """Service for calculating type effectiveness."""

    _effectiveness_matrix = None
    _type_names = None

    @classmethod
    def _build_effectiveness_matrix(cls) -> Dict[str, Dict[str, float]]:
        """Build a matrix of type effectiveness relationships."""
        if cls._effectiveness_matrix is not None:
            return cls._effectiveness_matrix

        # Build the matrix from database
        matrix = {}
        all_types = PokemonType.objects.all()

        for attacking_type in all_types:
            matrix[attacking_type.name] = {}
            damage_relations = attacking_type.damage_relations

            # Initialize all matchups to 1.0 (neutral)
            for defending_type in all_types:
                matrix[attacking_type.name][defending_type.name] = 1.0

            # Apply double damage
            for double_damage in damage_relations.get("double_damage_to", []):
                matrix[attacking_type.name][double_damage["name"]] = 2.0

            # Apply half damage
            for half_damage in damage_relations.get("half_damage_to", []):
                matrix[attacking_type.name][half_damage["name"]] = 0.5

            # Apply no damage
            for no_damage in damage_relations.get("no_damage_to", []):
                matrix[attacking_type.name][no_damage["name"]] = 0.0

        cls._effectiveness_matrix = matrix
        return matrix

    @classmethod
    def calculate_effectiveness(
        cls, attacking_type: str, defending_types: List[str]
    ) -> float:
        """Calculate effectiveness of an attacking type against defending types."""
        matrix = cls._build_effectiveness_matrix()
        effectiveness = 1.0

        for defending_type in defending_types:
            effectiveness *= matrix.get(attacking_type, {}).get(defending_type, 1.0)

        return effectiveness

    @classmethod
    def get_all_type_names(cls) -> Set[str]:
        """Get all type names."""
        if cls._type_names is not None:
            return cls._type_names

        cls._type_names = set(cls._build_effectiveness_matrix().keys())
        return cls._type_names
