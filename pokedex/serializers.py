from rest_framework import serializers

from pokedex.models import Ability, Pokemon, PokemonStats, PokemonType


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PokemonType
        fields = ["name"]


class AbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ability
        fields = ["name"]

class PokemonListSerializer(serializers.ModelSerializer):
    types = TypeSerializer(many=True, read_only=True)
    abilities = AbilitySerializer(many=True, read_only=True)

    class Meta:
        model = Pokemon
        fields = ["id", "name", "image_url", "types", "abilities"]


class PokemonTeamSynergySerializer(serializers.ModelSerializer):
    types = TypeSerializer(many=True, read_only=True)

    class Meta:
        model = Pokemon
        fields = ["id", "name", "types", "image_url"]


class PokemonStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PokemonStats
        fields = ["hp", "attack", "defense", "special_attack", "special_defense", "speed", "total"]


class PokemonDetailSerializer(serializers.ModelSerializer):
    types = TypeSerializer(many=True, read_only=True)
    abilities = AbilitySerializer(many=True, read_only=True)
    stats = PokemonStatsSerializer(read_only=True)

    class Meta:
        model = Pokemon
        fields = ["id", "name", "height", "weight", "image_url", "types", "abilities", "stats"]



