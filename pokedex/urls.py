from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from pokedex.views.pokedex import (
    PokedexView,
    PokemonDetailView,
    PokemonTeamSynergyView,
    PokemonComparisonView,
)

urlpatterns = [
    path("", PokedexView.as_view(), name="pokedex"),
    path("<int:pk>/", PokemonDetailView.as_view(), name="pokemon-detail"),
    path("team-synergy/", PokemonTeamSynergyView.as_view(), name="pokemon-team-synergy"),
    path("compare/", PokemonComparisonView.as_view(), name="compare"),
]
