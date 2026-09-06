"""Strategy 3 - Trigram Similarity (pg_trgm extension).

pg_trgm splits strings into groups of three characters and compares the sets of
trigrams. The result is an approximate search that tolerates typos
(`autentication` ~ `authentication`) and small variations.

We compare the query against the title AND the description, and keep the better
of the two scores (`Greatest`). The threshold avoids returning the whole catalog
with a tiny score.

Limitation: purely lexical (surface resemblance). A long natural-language query
yields low scores; there is no understanding of meaning.
"""

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Greatest

from articles.models import Article

from .base import SearchResult, all_articles

SIMILARITY_THRESHOLD = 0.1


def search(query: str) -> list[SearchResult]:
    if not query:
        return all_articles()

    similarity = Greatest(
        TrigramSimilarity("title", query),
        TrigramSimilarity("description", query),
    )
    queryset = (
        Article.objects.annotate(similarity=similarity)
        .filter(similarity__gt=SIMILARITY_THRESHOLD)
        .order_by("-similarity")
    )
    return [
        SearchResult(
            article, score=round(article.similarity, 4), score_label="similarity"
        )
        for article in queryset
    ]
