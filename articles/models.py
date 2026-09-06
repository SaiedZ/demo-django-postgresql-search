from django.conf import settings
from django.db import models
from pgvector.django import VectorField


class Article(models.Model):
    """A technical blog article. `embedding` is only used by semantic search."""

    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Migrations freeze the dimension, so changing the model needs a new one.
    embedding = VectorField(dimensions=settings.EMBEDDING_DIM, null=True, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def embedding_source_text(self) -> str:
        """Text the article embedding is computed from."""
        return "\n".join(
            part for part in (self.title, self.description, self.content) if part
        )
