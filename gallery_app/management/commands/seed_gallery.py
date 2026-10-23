import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from gallery_app.models import Art_Work, Collection, UserInteraction
from gallery_app.seed_data import (
    CATALOG,
    COLLECTIONS,
    DEFAULT_DESCRIPTION,
    FEATURED_FILENAMES,
)


class Command(BaseCommand):
    help = "Load the demo catalogue and copy artwork images into MEDIA_ROOT."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fresh",
            action="store_true",
            help="Delete existing artworks, collections and interactions first.",
        )
        parser.add_argument(
            "--demo-interactions",
            action="store_true",
            help="Seed deterministic anonymous interactions so the recommender has signal.",
        )

    def handle(self, *args, **options):
        source_dir = Path(settings.BASE_DIR) / "static" / "img"
        target_dir = Path(settings.MEDIA_ROOT) / "artworks"
        target_dir.mkdir(parents=True, exist_ok=True)

        with transaction.atomic():
            if options["fresh"]:
                UserInteraction.objects.all().delete()
                Collection.objects.all().delete()
                Art_Work.objects.all().delete()

            created = 0
            for filename, record in CATALOG.items():
                source = source_dir / filename
                if not source.exists():
                    self.stdout.write(self.style.WARNING(f"missing image: {filename}"))
                    continue

                destination = target_dir / filename
                if not destination.exists():
                    shutil.copy2(source, destination)

                title, style, era, medium, description = record
                # Identify rows by their image file: titles are editable in the
                # admin, but the file name is stable and keeps seeding idempotent.
                artwork, was_created = Art_Work.objects.update_or_create(
                    art_image=f"artworks/{filename}",
                    defaults={
                        "art_title": title,
                        "artiste": "Unattributed",
                        "style": style,
                        "era": era,
                        "medium": medium,
                        "art_desc": description or DEFAULT_DESCRIPTION,
                        "art_image": f"artworks/{filename}",
                        "featured": filename in FEATURED_FILENAMES,
                    },
                )
                created += int(was_created)

            for collection_data in COLLECTIONS:
                collection, _ = Collection.objects.update_or_create(
                    name=collection_data["name"],
                    defaults={
                        "description": collection_data["description"],
                        "accent": collection_data["accent"],
                        "featured": collection_data["featured"],
                    },
                )
                artworks = Art_Work.objects.filter(style__in=collection_data["styles"])
                collection.artworks.set(artworks)

            if options["demo_interactions"]:
                self._seed_demo_interactions()

        self.stdout.write(
            self.style.SUCCESS(
                f"Catalogue ready: {Art_Work.objects.count()} artworks "
                f"({created} new), {Collection.objects.count()} collections, "
                f"{UserInteraction.objects.count()} interactions."
            )
        )

    def _seed_demo_interactions(self):
        self.stdout.write("Seeding demo interactions (anonymous sessions)...")
        artworks = list(Art_Work.objects.order_by("id"))
        if not artworks:
            return

        # Deterministic pseudo-interactions so popularity and collaborative
        # filtering have something to work with in a fresh install. Clear old
        # demo rows first: if the catalogue changes size, stale pairings would
        # otherwise pile up instead of being replaced.
        UserInteraction.objects.filter(session_key__startswith="demo-session-").delete()

        for session_index in range(6):
            session_key = f"demo-session-{session_index + 1}"
            offset = session_index * 7
            for position in range(10):
                artwork = artworks[(offset + position * 3) % len(artworks)]
                UserInteraction.objects.update_or_create(
                    session_key=session_key,
                    artwork=artwork,
                    defaults={
                        "liked": position % 3 == 0,
                        "bookmarked": position % 5 == 0,
                        "view_count": (position + session_index) % 4,
                    },
                )
