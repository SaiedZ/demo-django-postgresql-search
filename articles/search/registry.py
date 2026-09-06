"""Catalog of search strategies.

Single source of truth for:
- the <select> on the main page,
- the explanation sentence shown under the selector,
- the column order on the Compare page.
"""

from . import contains, full_text, semantic, trigram

STRATEGIES = {
    "contains": {
        "label": "Contains",
        "description": (
            "Naive substring search (icontains) over the title, description and "
            "content. Easy to understand, but no typo tolerance and no relevance "
            "ranking."
        ),
        "module": contains,
    },
    "full_text": {
        "label": "PostgreSQL Full Text",
        "description": (
            "Native PostgreSQL Full Text Search: lexemes + stemming, insensitive "
            "to word order, ranked by relevance (title > description > content)."
        ),
        "module": full_text,
    },
    "trigram": {
        "label": "Trigram Similarity",
        "description": (
            "pg_trgm extension: compares groups of 3 characters. Tolerates typos "
            "and close variants, ranked by similarity score."
        ),
        "module": trigram,
    },
    "semantic": {
        "label": "Semantic / Embeddings",
        "description": (
            "Vector similarity (pgvector, cosine distance) over embeddings. "
            "Understands intent and synonyms, but less precise on an exact "
            "technical identifier."
        ),
        "module": semantic,
    },
}

DEFAULT_STRATEGY = "contains"
COMPARE_ORDER = ["contains", "full_text", "trigram", "semantic"]
