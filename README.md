# EsCurator API

The Django REST API behind EsCurator - a small art gallery with an explainable,
hybrid recommender.

It serves the catalogue, curated shelves, anonymous interaction tracking,
recommendations, taste profiles and session-based auth. No ML runtime, no
model files, no external services: the recommender is plain, testable Python.

## Highlights

- **55 seeded works**, 5 curated shelves, 14 styles and demo interaction data
  from a single command.
- **Explainable recommendations** with a reason for every pick, combining
  content similarity, collaborative co-occurrence and popularity.
- **Anonymous sessions** - `X-Session-Id` header, validated server-side. Likes,
  saves and views are stored per session without requiring an account.
- **19 tests** covering the catalogue, interactions, recommender and auth.
- **Production-shaped settings** - environment-driven config, WhiteNoise,
  PostgreSQL via `DATABASE_URL`, Gunicorn, and no secrets in the repo.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Windows: copy .env.example .env
# macOS/Linux: cp .env.example .env
python manage.py migrate
python manage.py seed_gallery --demo-interactions
python manage.py runserver
```

- API: `http://127.0.0.1:8000/api/`
- Admin: `http://127.0.0.1:8000/admin/` (create a login with
  `python manage.py createsuperuser`)
- Health check: `http://127.0.0.1:8000/api/health/`

### Seeding

```bash
python manage.py seed_gallery                     # catalogue + shelves
python manage.py seed_gallery --demo-interactions # + 60 anonymous signals
python manage.py seed_gallery --fresh             # wipe and reseed
```

Seeding is idempotent. It identifies works by their image file, copies images
from `static/img/` into `media/artworks/`, and replaces demo interactions
instead of accumulating them.

## Configuration

All settings have local defaults; override them with real environment
variables or a `.env` file.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | insecure dev key | **Set in production** |
| `DJANGO_DEBUG` | `true` | Set `false` in production |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Comma-separated hosts |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | local Vite origins | Comma-separated origins |
| `CORS_ALLOWED_ORIGINS` | local Vite origins | Frontend origins allowed to call the API |
| `DATABASE_URL` | empty (SQLite) | e.g. `postgres://user:pass@host:5432/db` |
| `REC_LIKE_WEIGHT` | `3.0` | Interaction weight for likes |
| `REC_BOOKMARK_WEIGHT` | `2.5` | Interaction weight for bookmarks |
| `REC_VIEW_WEIGHT` | `0.2` | Interaction weight for views |
| `LOG_LEVEL` | `INFO` | Root logger level |

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/art_works/` | Paginated catalogue (12/page). Filters: `search`, `style`, `era`, `artist`, `collection`, `featured`, `ordering` |
| `GET` | `/api/art_works/:id/` | One work, with counts and `is_liked` / `is_bookmarked` |
| `GET` | `/api/art_works/:id/similar/` | Similar works with reasons |
| `GET` | `/api/collections/` | Shelves with cover, tags and artwork counts |
| `GET` | `/api/collections/:slug/` | One shelf |
| `GET` | `/api/facets/` | Style and era counts for filters |
| `GET` | `/api/stats/` | Catalogue totals |
| `GET` | `/api/interactions/` | The session's interactions |
| `POST` | `/api/interactions/` | `{"artwork": 1, "type": "like" \| "bookmark" \| "view"}` |
| `POST` | `/api/recommendations/` | `{"limit": 8}` returns ranked works with `reason` |
| `GET` | `/api/taste/` | Top styles, eras and tags for the session |
| `GET` | `/api/health/` | Liveness probe |
| `POST` | `/api/auth/register/` | Session login after registration |
| `POST` | `/api/auth/login/` | Session login |
| `POST` | `/api/auth/logout/` | Session logout |
| `GET` | `/api/auth/me/` | Current user |

### Anonymous sessions

Every request from the frontend includes:

```
X-Session-Id: 8-64 characters from [A-Za-z0-9_-]
```

The backend rejects malformed values with `400`. A missing header is allowed
for read-only browsing; recommendations then fall back to curator picks.

## The recommender

`gallery_app/recommendations.py`

```
score = 0.55 * content + 0.25 * collaborative + 0.20 * popularity
```

- **Content** - Jaccard similarity over a work's style, era, medium, artist and
  tags against the session's liked/saved works (weighted by interaction type).
- **Collaborative** - co-occurrence with other sessions that share at least one
  engaged work.
- **Popularity** - damped likes, saves and views; also the cold-start signal
  alongside featured works.
- **Reasons** - generated from the strongest contributing signal, e.g.
  _"Because you liked Bungo Province"_, so the UI can show its work.

Every candidate is annotated with counts in a small number of queries; the
ranking itself runs in memory over at most a few hundred rows.

## Tests

```bash
python manage.py test
```

```
Found 19 test(s).
Ran 19 tests in 1.9s
OK
```

Coverage includes catalogue filtering and search, interaction toggles and
session isolation, recommendation shape/reasons/limits, similar works, facets,
stats, health, and register/login/logout/me.

## Project structure

```
art_recommendation_system/
|-- art_recommendation_system/   # settings, urls, wsgi
|-- gallery_app/
|   |-- management/commands/seed_gallery.py
|   |-- migrations/
|   |-- admin.py
|   |-- models.py                # Art_Work, Collection, UserInteraction
|   |-- recommendations.py       # hybrid recommender + taste profile
|   |-- seed_data.py             # 55-work demo catalogue
|   |-- serializers.py
|   |-- tests.py
|   `-- views.py
|-- members/                     # session auth API
|-- static/img/                  # public-domain source images
|-- build.sh / Procfile          # Render/Railway-style deployment
`-- requirements.txt
```

## Deployment

1. Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`,
   `CORS_ALLOWED_ORIGINS` and `DATABASE_URL`.
2. Run `./build.sh` (installs dependencies, collects static files, migrates,
   seeds) or wire the commands into your platform's build step.
3. Start with `gunicorn art_recommendation_system.wsgi`.
4. Serve `/media` from object storage or a reverse proxy; Django only serves
   it in development. `seed_gallery` copies the demo images into `MEDIA_ROOT`,
   which is ephemeral on most platforms.

## Honest notes

- Artist attribution was missing from the source archive, so the seed data
  says **Unattributed** rather than guessing.
- Style and era labels are illustrative demo metadata, editable in the admin.
- `interactions.csv` is a legacy export from the original project and is not
  used by the current code.
- Accounts exist as a session API, but the product is designed to work
  anonymously first.
