from dataclasses import dataclass

from articles.models import Article


@dataclass
class SearchResult:
    """Unified result type shared by every strategy.

    - `article`     : the matched Article object
    - `score`       : relevance / similarity (None if the strategy produces none)
    - `score_label` : human-readable name of the score, shown in the template
    """

    article: Article
    score: float | None = None
    score_label: str = ""


def all_articles() -> list[SearchResult]:
    """Common response when no query is given: every article."""
    return [SearchResult(article) for article in Article.objects.all()]
