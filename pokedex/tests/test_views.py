from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from pokedex.models import Ability, Pokemon, PokemonStats, PokemonType
from services.utils.pokemon_comparator import PokemonComparator
from services.utils.team_synergy_analyzer import TeamAnalysisService

User = get_user_model()


class PokedexBaseTestCase(APITestCase):
    """Base test case with setup data"""

    def setUp(self):
        # Create test types
        self.fire_type = PokemonType.objects.create(
            name="fire",
            damage_relations={
                "double_damage_to": [{"name": "grass"}, {"name": "bug"}],
                "half_damage_to": [{"name": "fire"}, {"name": "water"}],
                "no_damage_to": [],
            },
        )

        self.water_type = PokemonType.objects.create(
            name="water",
            damage_relations={
                "double_damage_to": [{"name": "fire"}, {"name": "rock"}],
                "half_damage_to": [{"name": "water"}, {"name": "grass"}],
                "no_damage_to": [],
            },
        )

        self.grass_type = PokemonType.objects.create(
            name="grass",
            damage_relations={
                "double_damage_to": [{"name": "water"}, {"name": "rock"}],
                "half_damage_to": [{"name": "grass"}, {"name": "fire"}],
                "no_damage_to": [],
            },
        )

        self.electric_type = PokemonType.objects.create(
            name="electric",
            damage_relations={
                "double_damage_to": [{"name": "water"}, {"name": "flying"}],
                "half_damage_to": [{"name": "electric"}, {"name": "grass"}],
                "no_damage_to": [{"name": "ground"}],
            },
        )

        # Create test abilities
        self.blaze = Ability.objects.create(name="blaze")
        self.torrent = Ability.objects.create(name="torrent")
        self.overgrow = Ability.objects.create(name="overgrow")

        # Create test Pokémon
        self.charizard = Pokemon.objects.create(
            name="charizard",
            height=17,
            weight=905,
            image_url="https://example.com/charizard.png",
        )
        self.charizard.types.add(self.fire_type)
        self.charizard.abilities.add(self.blaze)

        self.blastoise = Pokemon.objects.create(
            name="blastoise",
            height=16,
            weight=855,
            image_url="https://example.com/blastoise.png",
        )
        self.blastoise.types.add(self.water_type)
        self.blastoise.abilities.add(self.torrent)

        self.venusaur = Pokemon.objects.create(
            name="venusaur",
            height=20,
            weight=1000,
            image_url="https://example.com/venusaur.png",
        )
        self.venusaur.types.add(self.grass_type)
        self.venusaur.abilities.add(self.overgrow)

        # Create stats for Pokémon
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

        PokemonStats.objects.create(
            pokemon=self.blastoise,
            hp=79,
            attack=83,
            defense=100,
            special_attack=85,
            special_defense=105,
            speed=78,
            total=530,
        )

        PokemonStats.objects.create(
            pokemon=self.venusaur,
            hp=80,
            attack=82,
            defense=83,
            special_attack=100,
            special_defense=100,
            speed=80,
            total=525,
        )

        self.client = APIClient()


class PokedexViewTests(PokedexBaseTestCase):
    """Test the Pokedex list view"""

    def test_get_all_pokemon(self):
        """Test retrieving all Pokémon"""
        url = reverse("pokedex")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)


    def test_filter_by_name(self):
        """Test filtering Pokémon by name"""
        url = reverse("pokedex") + "?name=char"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "charizard")


    def test_filter_by_type(self):
        """Test filtering Pokémon by type"""
        url = reverse("pokedex") + f"?types={self.fire_type.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "charizard")


class PokemonDetailViewTests(PokedexBaseTestCase):
    """Test the Pokémon detail view"""

    def test_get_pokemon_detail(self):
        """Test retrieving a specific Pokémon's details"""
        url = reverse("pokemon-detail", kwargs={"pk": self.charizard.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "charizard")
        self.assertEqual(response.data["height"], 17)
        self.assertEqual(response.data["weight"], 905)
        self.assertEqual(len(response.data["types"]), 1)
        self.assertEqual(response.data["types"][0]["name"], "fire")
        self.assertEqual(len(response.data["abilities"]), 1)
        self.assertEqual(response.data["abilities"][0]["name"], "blaze")
        self.assertIsNotNone(response.data["stats"])


class TeamSynergyViewTests(PokedexBaseTestCase):
    """Test the team synergy analysis view"""

    def test_team_synergy_analysis(self):
        """Test team synergy analysis with valid Pokémon"""
        url = reverse("team-synergy")
        data = {
            "pokemons": [
                self.charizard.id,
                self.blastoise.id,
                self.venusaur.id,
                self.charizard.id,
                self.blastoise.id,
                self.venusaur.id,
            ]
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("score", response.data)
        self.assertIn("suggestions", response.data)
        self.assertIn("major_threats", response.data)
        self.assertIn("balanced_matchups", response.data)
        self.assertIn("safe_matchups", response.data)
        self.assertEqual(len(response.data["team"]), 6)


    def test_team_synergy_with_names(self):
        """Test team synergy analysis with Pokémon names"""
        url = reverse("team-synergy")
        data = {
            "pokemons": [
                "charizard",
                "blastoise",
                "venusaur",
                "charizard",
                "blastoise",
                "venusaur",
            ]
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["team"]), 6)


    def test_team_synergy_missing_pokemon(self):
        """Test team synergy analysis with missing Pokémon"""
        url = reverse("team-synergy")
        data = {"pokemons": [999]}  # Non-existent ID

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


    def test_team_synergy_wrong_count(self):
        """Test team synergy analysis with wrong number of Pokémon"""
        url = reverse("team-synergy")
        data = {"pokemons": [self.charizard.id]}  # Only 1 Pokémon

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


    def test_team_synergy_empty_request(self):
        """Test team synergy analysis with empty request"""
        url = reverse("team-synergy")
        data = {"pokemons": []}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class PokemonComparisonViewTests(PokedexBaseTestCase):
    """Test the Pokémon comparison view"""

    def test_pokemon_comparison(self):
        """Test comparing two Pokémon"""
        url = reverse("compare") + "?p1=charizard&p2=blastoise"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("comparison", response.data)
        self.assertIn("total", response.data)
        self.assertIn("roles", response.data)
        self.assertIn("overall_winner", response.data)


    def test_pokemon_comparison_missing_params(self):
        """Test comparison with missing parameters"""
        url = reverse("compare") + "?p1=charizard"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


    def test_pokemon_comparison_invalid_pokemon(self):
        """Test comparison with invalid Pokémon"""
        url = reverse("compare") + "?p1=charizard&p2=missingno"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_pokemon_comparison_missing_stats(self):
        """Test comparison with Pokémon missing stats"""
        # Create a Pokémon without stats
        pikachu = Pokemon.objects.create(
            name="pikachu",
            height=4,
            weight=60,
            image_url="https://example.com/pikachu.png",
        )
        pikachu.types.add(self.electric_type)

        url = reverse("compare") + "?p1=charizard&p2=pikachu"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class TeamAnalysisServiceTests(PokedexBaseTestCase):
    """Test the TeamAnalysisService"""

    def test_analyze_team_synergy(self):
        """Test team synergy analysis service"""
        team = [self.charizard, self.blastoise, self.venusaur]
        analysis = TeamAnalysisService.analyze_team_synergy(team)

        self.assertIn("score", analysis)
        self.assertIn("suggestions", analysis)
        self.assertIn("major_threats", analysis)
        self.assertIn("balanced_matchups", analysis)
        self.assertIn("safe_matchups", analysis)
        self.assertIsInstance(analysis["score"], int)
        self.assertIsInstance(analysis["suggestions"], list)


    def test_analyze_empty_team(self):
        """Test team synergy analysis with empty team"""
        analysis = TeamAnalysisService.analyze_team_synergy([])

        self.assertEqual(analysis["score"], 0)
        self.assertEqual(len(analysis["suggestions"]), 0)
        self.assertEqual(len(analysis["major_threats"]), 0)
        self.assertEqual(len(analysis["balanced_matchups"]), 0)
        self.assertEqual(len(analysis["safe_matchups"]), 0)


class PokemonComparatorTests(PokedexBaseTestCase):
    """Test the PokemonComparator"""

    def test_pokemon_comparison(self):
        """Test comparing two Pokémon"""
        comparator = PokemonComparator(self.charizard, self.blastoise)
        result = comparator.run()

        self.assertIn("comparison", result)
        self.assertIn("total", result)
        self.assertIn("roles", result)
        self.assertIn("overall_winner", result)

        # Check that all stats are compared
        self.assertEqual(len(result["comparison"]), 6)

        # Check that roles are assigned
        self.assertIn(self.charizard.name, result["roles"])
        self.assertIn(self.blastoise.name, result["roles"])


    def test_compare_stats(self):
        """Test stat comparison method"""
        comparator = PokemonComparator(self.charizard, self.blastoise)
        comparison = comparator.compare_stats()

        self.assertEqual(len(comparison), 6)
        for stat, data in comparison.items():
            self.assertIn(
                stat,
                [
                    "hp",
                    "attack",
                    "defense",
                    "special_attack",
                    "special_defense",
                    "speed",
                ],
            )
            self.assertIn(self.charizard.name, data)
            self.assertIn(self.blastoise.name, data)
            self.assertIn("winner", data)


    def test_total_comparison(self):
        """Test total stat comparison method"""
        comparator = PokemonComparator(self.charizard, self.blastoise)
        total = comparator.total_comparison()

        self.assertIn(self.charizard.name, total)
        self.assertIn(self.blastoise.name, total)
        self.assertIn("winner", total)


    def test_classify_role(self):
        """Test role classification method"""
        comparator = PokemonComparator(self.charizard, self.blastoise)

        # Test role classification for each Pokémon
        charizard_role = comparator.classify_role(self.charizard.stats)
        blastoise_role = comparator.classify_role(self.blastoise.stats)

        self.assertIn(charizard_role, ["Offensive", "Defensive", "Tank", "Balanced"])
        self.assertIn(blastoise_role, ["Offensive", "Defensive", "Tank", "Balanced"])
