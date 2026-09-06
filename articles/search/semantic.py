"""Strategy 4 - Semantic search with embeddings (pgvector).

Idea: each article is represented by a vector that captures its *meaning*
(computed from title + description + content, see the `load_demo_articles`
command). At search time we compute the query vector and look for the closest
articles using cosine distance (`CosineDistance` from pgvector).

Strengths: understands intent and synonyms ("make my site faster" -> articles
about caching / Core Web Vitals), even with no shared word.

Limitations: an exact identifier (`ERR_CONNECTION_RESET`, `select_related`) is
often better served by Contains/Trigram; the score depends on the model; picking
a threshold is tricky (here we set none and just return the closest ones).
"""

from pgvector.django import CosineDistance

from articles.models import Article

from .base import SearchResult, all_articles
from .embeddings import get_embedder

TOP_K = 15


def search(query: str) -> list[SearchResult]:
    if not query:
        return all_articles()

    query_vector = get_embedder().embed(query)

    queryset = (
        Article.objects.filter(embedding__isnull=False)
        .annotate(distance=CosineDistance("embedding", query_vector))
        .order_by("distance")[:TOP_K]
    )

    results = []
    for article in queryset:
        # cosine distance is in [0, 2]; similarity = 1 - distance is in [-1, 1].
        similarity = 1 - article.distance
        results.append(
            SearchResult(
                article, score=round(similarity, 4), score_label="cosine similarity"
            )
        )
    return results
