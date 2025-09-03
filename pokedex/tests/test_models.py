from django.test import TestCase

from pokedex.models import Ability, Pokemon, PokemonStats, PokemonType


class PokemonModelTests(TestCase):
    """Test the Pokemon model"""

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


    def test_pokemon_creation(self):
        """Test creating a Pokémon"""
        self.assertEqual(self.charizard.name, "charizard")
        self.assertEqual(self.charizard.height, 17)
        self.assertEqual(self.charizard.weight, 905)


    def test_pokemon_types(self):
        """Test Pokémon type relationships"""
        self.assertEqual(self.charizard.types.count(), 1)
        self.assertEqual(self.charizard.types.first().name, "fire")


    def test_pokemon_abilities(self):
        """Test Pokémon ability relationships"""
        self.assertEqual(self.charizard.abilities.count(), 1)
        self.assertEqual(self.charizard.abilities.first().name, "blaze")


    def test_get_pokemon_by_id(self):
        """Test getting Pokémon by ID"""
        pokemon = Pokemon.get_pokemon(str(self.charizard.id))
        self.assertEqual(pokemon, self.charizard)


    def test_get_pokemon_by_name(self):
        """Test getting Pokémon by name"""
        pokemon = Pokemon.get_pokemon("charizard")
        self.assertEqual(pokemon, self.charizard)


    def test_pokemon_str_representation(self):
        """Test Pokémon string representation"""
        self.assertEqual(str(self.charizard), "charizard")


class PokemonStatsModelTests(TestCase):
    """Test the PokemonStats model"""

    def setUp(self):
        self.charizard = Pokemon.objects.create(
            name="charizard",
            height=17,
            weight=905,
        )

        self.stats = PokemonStats.objects.create(
            pokemon=self.charizard,
            hp=78,
            attack=84,
            defense=78,
            special_attack=109,
            special_defense=85,
            speed=100,
            total=534,
        )


    def test_stats_creation(self):
        """Test creating Pokémon stats"""
        self.assertEqual(self.stats.hp, 78)
        self.assertEqual(self.stats.attack, 84)
        self.assertEqual(self.stats.defense, 78)
        self.assertEqual(self.stats.special_attack, 109)
        self.assertEqual(self.stats.special_defense, 85)
        self.assertEqual(self.stats.speed, 100)
        self.assertEqual(self.stats.total, 534)


    def test_stats_str_representation(self):
        """Test stats string representation"""
        self.assertEqual(str(self.stats), "charizard Stats")
