"""Load the demo articles and (re)compute their embeddings.

Idempotent: articles are matched by title, so re-running never duplicates data.
Use --skip-embeddings when sentence-transformers is not installed.
"""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from articles.models import Article

DEFAULT_PATH = Path(settings.BASE_DIR) / "articles" / "fixtures" / "demo_articles.json"


class Command(BaseCommand):
    help = "Load the demo articles and compute their embeddings."

    def add_arguments(self, parser):
        parser.add_argument("--path", default=str(DEFAULT_PATH))
        parser.add_argument("--skip-embeddings", action="store_true")

    def handle(self, *args, **options):
        path = Path(options["path"])
        articles = json.loads(path.read_text(encoding="utf-8"))

        embedder = None
        if not options["skip_embeddings"]:
            from articles.search.embeddings import get_embedder

            self.stdout.write("Loading the embedding model...")
            embedder = get_embedder()

        created = updated = 0
        for item in articles:
            article, was_created = Article.objects.update_or_create(
                title=item["title"],
                defaults={
                    "description": item.get("description", ""),
                    "content": item.get("content", ""),
                },
            )
            if embedder is not None:
                article.embedding = embedder.embed(article.embedding_source_text())
                article.save(update_fields=["embedding"])

            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"{created} article(s) created, {updated} updated"
                + ("" if embedder else " (embeddings skipped)")
            )
        )
