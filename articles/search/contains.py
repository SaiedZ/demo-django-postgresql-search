"""Strategy 1 - Contains (naive substring search).

`icontains` compiles to `ILIKE '%term%'` in SQL. Simple, predictable, zero
configuration. But: sensitive to the exact character order, handles neither
typos nor grammatical variants (query != queries), and does not rank results by
relevance.
"""

from django.db.models import Q

from articles.models import Article

from .base import SearchResult, all_articles


def search(query: str) -> list[SearchResult]:
    if not query:
        return all_articles()

    filters = (
        Q(title__icontains=query)
        | Q(description__icontains=query)
        | Q(content__icontains=query)
    )
    return [SearchResult(article) for article in Article.objects.filter(filters)]
