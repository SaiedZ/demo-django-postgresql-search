"""Minimal abstraction for generating embeddings.

Goal: isolate "how a piece of text becomes a vector" so the local model can
later be swapped for an API (OpenAI, Cohere, ...) without touching the rest of
the code.

Embedder contract: an `embed(text: str) -> list[float]` method returning a
vector of dimension `settings.EMBEDDING_DIM`, normalized (L2 norm = 1) so the
cosine distance is directly interpretable.

Default: the "local" backend => sentence-transformers, no network call.
"""

from functools import lru_cache

from django.conf import settings


class LocalSentenceTransformerEmbedder:
    """Model running on this machine. The first call downloads the model
    (~90 MB for all-MiniLM-L6-v2), then everything happens offline."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        vector = self._model.encode(text or "", normalize_embeddings=True)
        return vector.tolist()


# --- Example for plugging in an API later (kept commented on purpose) ---
# class OpenAIEmbedder:
#     def __init__(self, model: str = "text-embedding-3-small"):
#         from openai import OpenAI
#         self._client = OpenAI()  # reads OPENAI_API_KEY from the environment
#         self._model = model
#
#     def embed(self, text: str) -> list[float]:
#         response = self._client.embeddings.create(model=self._model, input=text or "")
#         return response.data[0].embedding
#
# You would also need to adjust EMBEDDING_DIM (1536 for text-embedding-3-small)
# and create a migration on Article.embedding.


@lru_cache(maxsize=1)
def get_embedder():
    """Return the configured embedder. Cached: the local model is loaded only
    once per process."""
    backend = settings.EMBEDDING_BACKEND
    if backend == "local":
        return LocalSentenceTransformerEmbedder(settings.EMBEDDING_MODEL)
    # elif backend == "openai":
    #     return OpenAIEmbedder(settings.EMBEDDING_MODEL)
    raise ValueError(f"Unknown EMBEDDING_BACKEND: {backend!r}")
