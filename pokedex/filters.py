from django_filters import CharFilter, FilterSet, ModelMultipleChoiceFilter

from pokedex.models import Ability, Pokemon, PokemonType


class PokedexFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains", label="Name")
    types = ModelMultipleChoiceFilter(field_name="types", queryset=PokemonType.objects.all(), label="Types")
    abilities = ModelMultipleChoiceFilter(field_name="abilities", queryset=Ability.objects.all(), label="Abilities")


    class Meta:
        model = Pokemon
        fields = ["name", "types", "abilities"]
