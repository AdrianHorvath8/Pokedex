from django.db import models
from django.shortcuts import get_object_or_404


class PokemonType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    damage_relations = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name


class Ability(models.Model):
    name = models.CharField(max_length=50)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Pokemon(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    types = models.ManyToManyField(PokemonType, related_name="pokemon")
    abilities = models.ManyToManyField(Ability, related_name="pokemon")

    def __str__(self):
        return self.name

    @classmethod
    def get_pokemon(cls, identifier: str):
        """Helper to resolve Pokémon by ID or name."""
        if identifier.isdigit():
            return get_object_or_404(Pokemon, id=int(identifier))
        return get_object_or_404(Pokemon, name__iexact=identifier)


class PokemonStats(models.Model):
    pokemon = models.OneToOneField(Pokemon, on_delete=models.CASCADE, related_name="stats")
    hp = models.IntegerField(null=True, blank=True)
    attack = models.IntegerField(null=True, blank=True)
    defense = models.IntegerField(null=True, blank=True)
    special_attack = models.IntegerField(null=True, blank=True)
    special_defense = models.IntegerField(null=True, blank=True)
    speed = models.IntegerField(null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.pokemon.name} Stats"
