## Django Pokedex Challenge

Django REST API that integrates with the public PokeAPI to deliver a practical Pokedex. It includes:

- Robust async data ingestion (first 151 Pokémon) via a custom management command
- Filterable, paginated Pokémon listing and detail endpoints
- A team synergy analyzer powered by type effectiveness
- A head-to-head Pokémon comparison endpoint
- Dockerized development workflow

`For demonstration purposes, this project uses simplified configuration without environment variables for the SECRET_KEY and other settings, prioritizing ease of setup over production-grade security measures.`

### Tech Stack
- **Backend**: Django 5, Django REST Framework, django-filter
- **Async ingestion**: `aiohttp`, `asyncio`, `asgiref.sync`
- **DB**: SQLite (simple local/dev usage)
- **Containerization**: Docker + docker-compose

---

## Quick Start (Docker)

1) Build and run the app:

```bash
docker-compose up --build
```

2) Populate the local database with Pokémon data (required for endpoints to be useful):

```bash
docker-compose exec web python manage.py populate_pokedex
```

The API will be available at `http://localhost:8000/`.

---

## API Documentation

Base path: `http://localhost:8000/api/pokedex/`

### 1) List Pokémon
- **GET** `/api/pokedex/`
- Pagination: DRF PageNumberPagination (default page size: 20)
- Filters (via `django-filter`):
  - `name`: partial, case-insensitive match on Pokémon name
  - `types`: multiple type IDs allowed (e.g., `types=10&types=3`)
  - `abilities`: multiple ability IDs allowed (e.g., `abilities=65`)

Examples:

```bash
curl "http://localhost:8000/api/pokedex/?page=1&name=char"
curl "http://localhost:8000/api/pokedex/?types=10&types=3"
curl "http://localhost:8000/api/pokedex/?abilities=65"
```


### 2) Pokémon Detail
- **GET** `/api/pokedex/<id>/`

Example:
```bash
curl "http://localhost:8000/api/pokedex/60/"

```

### 3) Team Synergy Analysis
- **POST** `/api/pokedex/team-synergy/`
- Body: provide exactly 6 Pokémon (IDs or names)

Example:
```bash
curl -X POST "http://localhost:8000/api/pokedex/team-synergy/" \
  -H "Content-Type: application/json" \
  -d '{
    "pokemons": ["meowth", "vaporeon", "abra", "pikachu", "psyduck", "golduck"]
  }'
```

### 4) Compare Two Pokémon
- **GET** `/api/pokedex/compare/?p1=<name-or-id>&p2=<name-or-id>`

Example:
```bash
curl "http://localhost:8000/api/pokedex/compare/?p1=charizard&p2=blastoise"
```

---

## Data Ingestion Details

The management command `populate_pokedex` asynchronously retrieves:

- Pokémon 1–151 (`/pokemon/{id}`)
- Type damage relations for all discovered types (`/type/{name}`)

It persists:
- Core Pokémon attributes (name, height, weight, sprite URL)
- Many-to-many relations for types and abilities
- A `PokemonStats` one-to-one record with derived `total`
- Type `damage_relations` JSON used to build an in-memory effectiveness matrix

Command to run:
```bash
docker-compose exec web python manage.py populate_pokedex
```

---

## Architecture Notes

- `pokedex` app exposes the REST API (views, serializers, filters, urls)
- `services` app encapsulates domain logic:
  - `TypeEffectivenessService`: builds an effectiveness matrix from stored type relations
  - `TeamAnalysisService`: computes team threats, safe matchups, suggestions, and a synergy score
  - `PokemonComparator`: compares two Pokémon on per-stat and overall basis and infers coarse roles
- Pagination and filtering are configured globally in `settings.py`

---

## Testing

Run tests:
```bash
docker-compose exec web python manage.py test
```

---

## Submission & Notes

- Make sure to run the population command before exploring the API.
- You can explore all API endpoints through Django REST Framework's intuitive browsable interface, which provides instant documentation and testing capabilities for the robust backend services I've built.
- Dockerized workflow is the recommended path for a clean start.

