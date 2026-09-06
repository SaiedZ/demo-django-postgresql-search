"""Strategy 2 - PostgreSQL Full Text Search.

PostgreSQL turns text into a `tsvector` (normalized lexemes + stemming) and the
query into a `tsquery`. Upsides: insensitive to word order, handles grammatical
variants (optimize / optimizing / optimization), ranks by relevance via
`SearchRank`. We weight the title (A) above the description (B) and the content
(C).

Limitation: it does not fix typos, and "faster" will not match "performance"
(no synonym support without extra configuration).
"""

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from articles.models import Article

from .base import SearchResult, all_articles

# `english` = stemming dictionary used to build the lexemes.
_VECTOR = (
    SearchVector("title", weight="A", config="english")
    + SearchVector("description", weight="B", config="english")
    + SearchVector("content", weight="C", config="english")
)


def search(query: str) -> list[SearchResult]:
    if not query:
        return all_articles()

    search_query = SearchQuery(query, config="english")
    queryset = (
        Article.objects.annotate(vector=_VECTOR)
        # `vector=search_query` is the tsvector @@ tsquery match test: keep only
        # rows the query actually matches. Ranking alone is not a filter.
        .filter(vector=search_query)
        .annotate(rank=SearchRank(_VECTOR, search_query))
        .order_by("-rank")
    )
    return [
        SearchResult(article, score=round(article.rank, 4), score_label="rank")
        for article in queryset
    ]
