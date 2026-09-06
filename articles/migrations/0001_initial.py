"""Initial migration.

We first enable the two required PostgreSQL extensions:
- `vector`  (pgvector)  -> Article.embedding field + semantic search
- `pg_trgm`             -> TrigramSimilarity (strategy 3)

These operations run `CREATE EXTENSION IF NOT EXISTS ...`, so the PostgreSQL role
must be allowed to create an extension (that is the case for the default
superuser of the Docker image shipped with this project).
"""
import pgvector.django
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations, models
from pgvector.django import VectorExtension


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        VectorExtension(),
        TrigramExtension(),
        migrations.CreateModel(
            name="Article",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("content", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("embedding", pgvector.django.VectorField(blank=True, dimensions=384, null=True)),
            ],
            options={"ordering": ["title"]},
        ),
    ]
