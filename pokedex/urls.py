from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from pokedex.views.pokedex import (
    PokedexView,
    PokemonDetailView,
    TeamSynergyView,
    PokemonComparisonView,
)

urlpatterns = [
    path("", PokedexView.as_view(), name="pokedex"),
    path("<int:pk>/", PokemonDetailView.as_view(), name="pokemon-detail"),
    path("team-synergy/", TeamSynergyView.as_view(), name="team-synergy"),
    path("compare/", PokemonComparisonView.as_view(), name="compare"),
]
