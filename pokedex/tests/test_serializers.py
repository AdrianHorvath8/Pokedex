from django.test import TestCase

from pokedex.models import Ability, Pokemon, PokemonStats, PokemonType
from pokedex.serializers import (
    AbilitySerializer,
    PokemonDetailSerializer,
    PokemonListSerializer,
    PokemonStatsSerializer,
    PokemonTeamSynergySerializer,
    TypeSerializer,
)


class SerializerTests(TestCase):
    """Test the serializers"""

    def setUp(self):
        self.fire_type = PokemonType.objects.create(name="fire", damage_relations={})
        self.blaze = Ability.objects.create(name="blaze")

        self.charizard = Pokemon.objects.create(
            name="charizard",
            height=17,
            weight=905,
            image_url="https://example.com/charizard.png",
        )
        self.charizard.types.add(self.fire_type)
        self.charizard.abilities.add(self.blaze)

        PokemonStats.objects.create(
            pokemon=self.charizard,
            hp=78,
            attack=84,
            defense=78,
            special_attack=109,
            special_defense=85,
            speed=100,
            total=534,
        )


    def test_type_serializer(self):
        """Test TypeSerializer"""
        serializer = TypeSerializer(self.fire_type)
        data = serializer.data

        self.assertEqual(data["name"], "fire")


    def test_ability_serializer(self):
        """Test AbilitySerializer"""
        serializer = AbilitySerializer(self.blaze)
        data = serializer.data

        self.assertEqual(data["name"], "blaze")


    def test_stats_serializer(self):
        """Test PokemonStatsSerializer"""
        stats = self.charizard.stats
        serializer = PokemonStatsSerializer(stats)
        data = serializer.data

        self.assertEqual(data["hp"], 78)
        self.assertEqual(data["attack"], 84)
        self.assertEqual(data["defense"], 78)
        self.assertEqual(data["special_attack"], 109)
        self.assertEqual(data["special_defense"], 85)
        self.assertEqual(data["speed"], 100)
        self.assertEqual(data["total"], 534)


    def test_pokemon_list_serializer(self):
        """Test PokemonListSerializer"""
        serializer = PokemonListSerializer(self.charizard)
        data = serializer.data

        self.assertEqual(data["name"], "charizard")
        self.assertEqual(len(data["types"]), 1)
        self.assertEqual(data["types"][0]["name"], "fire")
        self.assertEqual(len(data["abilities"]), 1)
        self.assertEqual(data["abilities"][0]["name"], "blaze")


    def test_pokemon_detail_serializer(self):
        """Test PokemonDetailSerializer"""
        serializer = PokemonDetailSerializer(self.charizard)
        data = serializer.data

        self.assertEqual(data["name"], "charizard")
        self.assertEqual(data["height"], 17)
        self.assertEqual(data["weight"], 905)
        self.assertEqual(len(data["types"]), 1)
        self.assertEqual(data["types"][0]["name"], "fire")
        self.assertEqual(len(data["abilities"]), 1)
        self.assertEqual(data["abilities"][0]["name"], "blaze")
        self.assertIsNotNone(data["stats"])


    def test_pokemon_team_synergy_serializer(self):
        """Test PokemonTeamSynergySerializer"""
        serializer = PokemonTeamSynergySerializer(self.charizard)
        data = serializer.data

        self.assertEqual(data["name"], "charizard")
        self.assertEqual(len(data["types"]), 1)
        self.assertEqual(data["types"][0]["name"], "fire")
