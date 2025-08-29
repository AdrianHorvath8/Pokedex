from typing import Dict, List, Union

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from pokedex.filters import PokedexFilter
from pokedex.models import Pokemon, PokemonStats
from pokedex.serializers import (
    PokemonDetailSerializer,
    PokemonListSerializer,
    PokemonTeamSynergySerializer,
)
from services.utils.pokemon_comparator import PokemonComparator
from services.utils.team_synergy_analyzer import TeamAnalysisService


class PokedexView(generics.ListAPIView):
    queryset = Pokemon.objects.all().prefetch_related("types", "abilities")
    serializer_class = PokemonListSerializer
    filterset_class = PokedexFilter


class PokemonDetailView(generics.RetrieveAPIView):
    queryset = Pokemon.objects.all()
    serializer_class = PokemonDetailSerializer


class PokemonTeamSynergyView(APIView):
    """API endpoint for analyzing Pokémon team synergy."""

    def _get_pokemon_objects(self, pokemons: List[Union[int, str]]) -> List[Pokemon]:
        """Get Pokémon objects from a list of IDs or names."""
        team_pokemon = []

        for p in pokemons:
            try:
                if isinstance(p, int) or (isinstance(p, str) and p.isdigit()):
                    pokemon = Pokemon.objects.get(id=int(p))
                else:
                    pokemon = Pokemon.objects.get(name__iexact=p)
                team_pokemon.append(pokemon)
            except Pokemon.DoesNotExist:
                raise Pokemon.DoesNotExist(f"Pokémon '{p}' not found")

        return team_pokemon

    def post(self, request):
        """
        Analyze the synergy of a team of Pokémon.

        Request body should contain:
        {
            "pokemons": [1, 2, 3, 4, 5, 6]  # List of Pokémon IDs or names
        }
        """
        pokemons = request.data.get("pokemons", [])

        if not pokemons:
            return Response(
                {"error": "No Pokémon provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        if len(pokemons) != 6:
            return Response(
                {"error": "Exactly 6 Pokémon are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get Pokémon objects
        try:
            team_pokemon = self._get_pokemon_objects(pokemons)
        except Pokemon.DoesNotExist as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Analyze team synergy
        analysis = TeamAnalysisService.analyze_team_synergy(team_pokemon)

        # Prepare response data
        response_data = {
            "score": analysis["score"],
            "team": PokemonTeamSynergySerializer(team_pokemon, many=True).data,
            "suggestions": analysis["suggestions"],
            "major_threats": analysis["major_threats"],
            "balanced_matchups": analysis["balanced_matchups"],
            "safe_matchups": analysis["safe_matchups"],
        }

        return Response(response_data, status=status.HTTP_200_OK)


class PokemonComparisonView(APIView):
    """
    Compare two Pokémon by stats.
    Delegates actual comparison logic to PokemonComparator service.
    """

    def get(self, request, *args, **kwargs):
        p1_name = request.query_params.get("p1")
        p2_name = request.query_params.get("p2")

        if not p1_name or not p2_name:
            return Response(
                {"error": "Please provide ?p1=<pokemon1>&p2=<pokemon2>"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        p1, p2 = Pokemon.get_pokemon(p1_name), Pokemon.get_pokemon(p2_name)

        # Ensure both have stats
        if not hasattr(p1, "stats") or not hasattr(p2, "stats"):
            return Response(
                {"error": "One of the Pokémon has no stats saved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comparator = PokemonComparator(p1, p2)
        return Response(comparator.run())
