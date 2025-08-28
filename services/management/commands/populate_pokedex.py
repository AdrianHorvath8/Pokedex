import asyncio
import aiohttp
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from django.db import transaction

from pokedex.models import Ability, Pokemon, PokemonStats, PokemonType

STAT_MAP = {
    "hp": "hp",
    "attack": "attack",
    "defense": "defense",
    "special-attack": "special_attack",
    "special-defense": "special_defense",
    "speed": "speed",
}


class PokedexPopulator:
    """Handles fetching and saving Pokemon data from the PokeAPI."""

    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    async def fetch_data(self, session, url):
        """Fetch JSON data from a URL."""
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None

    @sync_to_async
    def save_pokemon(self, data):
        """Save a Pokemon to the database with its types and abilities."""
        with transaction.atomic():
            # Create or get the Pokemon
            pokemon, created = Pokemon.objects.get_or_create(
                name=data["name"],
                defaults={
                    "height": data["height"],
                    "weight": data["weight"],
                    "image_url": data["sprites"]["front_default"],
                }
            )

            if created:
                # prepare stats dict
                stats_dict = {}
                total = 0
                for stat_entry in data["stats"]:
                    stat_name = stat_entry["stat"]["name"]
                    base_value = stat_entry["base_stat"]

                    if stat_name in STAT_MAP:
                        stats_dict[STAT_MAP[stat_name]] = base_value
                        total += base_value

                stats_dict["total"] = total

                # create the PokemonStats record
                PokemonStats.objects.create(pokemon=pokemon, **stats_dict)

            # Add types
            for type_data in data["types"]:
                type_name = type_data["type"]["name"]
                type_obj, _ = PokemonType.objects.get_or_create(name=type_name)
                pokemon.types.add(type_obj)

            # Add abilities
            for ability_data in data["abilities"]:
                ability_name = ability_data["ability"]["name"]
                ability_obj, _ = Ability.objects.get_or_create(name=ability_name, is_hidden=ability_data["is_hidden"])
                pokemon.abilities.add(ability_obj)

            return pokemon

    @sync_to_async
    def save_type_details(self, data):
        """Save detailed type information to the database."""
        with transaction.atomic():
            try:
                type_obj = PokemonType.objects.get(name=data["name"])
                type_obj.damage_relations = data["damage_relations"]
                type_obj.save()
                return type_obj
            except PokemonType.DoesNotExist:
                self.stderr.write(f"PokemonType {data['name']} not found in database")
                return None

    @sync_to_async
    def get_all_types(self):
        """Get all Pokemon types from the database."""
        return list(PokemonType.objects.all())

    async def populate_pokemon(self, session):
        """Fetch and save all Pokemon data."""
        self.stdout.write("Fetching Pokemon data...")

        tasks = []
        for pokemon_id in range(1, 152):  # First generation
            task = asyncio.create_task(self.fetch_and_save_pokemon(session, pokemon_id))
            tasks.append(task)

        await asyncio.gather(*tasks)
        self.stdout.write("All Pokemon data saved successfully!")

    async def fetch_and_save_pokemon(self, session, pokemon_id):
        """Fetch and save a single Pokemon."""
        data = await self.fetch_data(session, f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/")

        if not data:
            self.stderr.write(f"Error fetching Pokemon #{pokemon_id}")
            return

        try:
            await self.save_pokemon(data)
        except Exception as e:
            self.stderr.write(f"Error saving Pokemon #{pokemon_id}: {str(e)}")

    async def populate_type_details(self, session):
        """Fetch and save detailed type information."""
        self.stdout.write("Fetching type details...")

        # Get all types from the database
        types = await self.get_all_types()

        tasks = []
        for type_obj in types:
            task = asyncio.create_task(self.fetch_and_save_type_details(session, type_obj.name))
            tasks.append(task)

        await asyncio.gather(*tasks)
        self.stdout.write("All type details saved successfully!")

    async def fetch_and_save_type_details(self, session, type_name):
        """Fetch and save details for a single type."""
        try:
            data = await self.fetch_data(session, f"https://pokeapi.co/api/v2/type/{type_name}/")
            if data:
                await self.save_type_details(data)
        except Exception as e:
            self.stderr.write(f"Error processing type {type_name}: {str(e)}")

    async def run(self):
        """Run the complete population process."""
        async with aiohttp.ClientSession() as session:
            # First, fetch and save all Pokemon
            await self.populate_pokemon(session)
            # Then, fetch and save type details
            await self.populate_type_details(session)


class Command(BaseCommand):
    """Django management command to populate the Pokedex."""
    
    help = 'Asynchronously populates the database with the first 151 Pokemon'
    
    def handle(self, *args, **options):
        self.stdout.write("Starting to populate Pokedex...")
        
        populator = PokedexPopulator(self.stdout, self.stderr)
        
        try:
            asyncio.run(populator.run())
            self.stdout.write(self.style.SUCCESS("Successfully populated Pokedex!"))
        except Exception as e:
            self.stderr.write(f"Failed to populate Pokedex: {str(e)}")
            raise
