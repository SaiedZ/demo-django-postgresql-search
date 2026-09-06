# demo_search_postgresql

A small **teaching** Django project that compares four search strategies
available with Django and PostgreSQL:

1. **Contains** – naive substring search (`icontains`)
2. **PostgreSQL Full Text** – `SearchVector` / `SearchQuery` / `SearchRank`
3. **Trigram Similarity** – `pg_trgm` extension, tolerant to typos
4. **Semantic / Embeddings** – vector similarity with `pgvector` + a local
   embedding model (`sentence-transformers`)

## 1. Teaching goal

To back a technical article. The central message:

> **Each search strategy answers a different problem.
> The best solution is the one that meets the need with justified complexity.**

Embeddings are **not** presented as a superior evolution over the other
approaches: they are excellent at intent and synonyms, and often worse than a
plain `LIKE` on a precise technical identifier.

The code is intentionally simple: no DRF, no Celery, no cache, no
authentication, no JavaScript frontend. Each strategy fits in a small module
under [`articles/search/`](articles/search/) that can be read and quoted on its
own.

## 2. Requirements

- Python 3.10+
- Docker + Docker Compose (for PostgreSQL only)
- ~150 MB of disk for the embedding model (downloaded on first use)

## 3. Start PostgreSQL

The [`pgvector/pgvector:pg16`](https://hub.docker.com/r/pgvector/pgvector) image
ships the `pgvector` extension; `pg_trgm` comes bundled with PostgreSQL. Both are
enabled automatically by the `0001_initial` migration.

```bash
cp .env.example .env        # adjust values if needed
docker compose up -d
```

## 4. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 5. Run migrations

```bash
python manage.py migrate
```

## 6. Load the demo data

```bash
python manage.py load_demo_articles
```

The command is **idempotent** (key: the article title): it can be re-run without
duplicating data. It also recomputes the embeddings. Without
`sentence-transformers`, use `--skip-embeddings` (semantic search will then be
empty).

## 7. Run Django

```bash
python manage.py runserver
```

- Main page: http://127.0.0.1:8000/
- Compare page: http://127.0.0.1:8000/compare/

## 8. Interesting queries to try

| Query | What it illustrates |
|---|---|
| `select_related` | exact technical term: Contains/Full-text find it, Semantic dilutes it |
| `ERR_CONNECTION_RESET` | precise identifier: Contains is unbeatable |
| `postgresql full text search` | several important words: Full-text ranks best |
| `Django query optimization` | words out of order + grammatical variant: Full-text finds "Optimizing Django database queries", Contains fails |
| `testing django models` | grammatical variant (`testing`/`tests`): Full-text via stemming |
| `autentication` | typo: only Trigram still finds the "authentication" articles |
| `make my website load faster` | synonyms / intent: Semantic surfaces caching and Core Web Vitals |
| `my Django application makes too many SQL queries` | intent without the exact words: Semantic surfaces the N+1 problem |

See [`SEARCH_COMPARISON.md`](SEARCH_COMPARISON.md) for the **actual** output of
every strategy on these queries (regenerate with `python manage.py search_report`).

## 9. Limitations of each strategy

**Contains (`icontains`)**
- handles neither typos nor grammatical variants (`query` != `queries`);
- sensitive to the exact character order;
- no relevance ranking;
- `ILIKE '%term%'` cannot use a plain B-tree index (sequential scan).

**PostgreSQL Full Text**
- no typo correction;
- no synonyms without a dedicated dictionary;
- here the `tsvector` is computed on the fly for every query: on a large volume
  it should be stored in a column + GIN index.

**Trigram Similarity**
- purely lexical (surface resemblance), no understanding of meaning;
- a long natural-language query yields low scores;
- the similarity threshold is arbitrary (here `0.1`) and depends on the data;
- needs a GIN/GiST `gin_trgm_ops` index to stay fast.

**Semantic / Embeddings**
- compute cost: one embedding per article, regenerated when the text changes;
- here embeddings are **not** re-synced automatically (you must re-run
  `load_demo_articles`);
- no distance threshold: we return the *k* nearest, even if none is really
  relevant;
- the choice of metric (cosine here) and of model changes the results;
- `all-MiniLM-L6-v2` is small: fine for a demo, below a large model or an API
  for production;
- no vector index (HNSW/IVFFlat): exact O(n) search, acceptable on 26 rows only.

## Summary table

Behaviors **actually observed** with the demo dataset (full details and scores
in [`SEARCH_COMPARISON.md`](SEARCH_COMPARISON.md)).

Legend: ✅✅ clearly best · ✅ works well · ⚠️ partial / noisy / threshold-dependent · ❌ fails

| Query type | Contains | Full Text | Trigram | Semantic |
|---|---|---|---|---|
| exact identifier (`ERR_CONNECTION_RESET`) | ✅✅ | ✅✅ | ⚠️ (+ noise) | ⚠️ (+ noise) |
| precise term (`select_related`) | ✅✅ | ✅✅ | ✅ | ⚠️ diluted |
| several words (`postgresql full text search`) | ❌ | ✅✅ | ⚠️ | ✅ |
| words out of order (`Django query optimization`) | ❌ | ✅✅ | ⚠️ | ✅ |
| grammatical variant (`testing` vs `tests`) | ❌ | ✅✅ | ⚠️ | ✅✅ |
| typo (`autentication`) | ❌ | ❌ | ✅✅ | ⚠️ low score |
| synonym (`make my website load faster`) | ❌ | ❌ | ⚠️ | ✅✅ |
| user intent (`too many SQL queries`) | ❌ | ❌ | ❌ | ✅✅ |
| common word, ranking (`authentication`) | ⚠️ no ranking | ✅✅ | ✅ | ✅ |

## Code structure

```
articles/
├── models.py                 Article (title, description, content, created_at, embedding)
├── views.py                  2 thin views: search_view / compare_view
├── search/
│   ├── base.py               SearchResult (shared return type)
│   ├── contains.py           strategy 1
│   ├── full_text.py          strategy 2
│   ├── trigram.py            strategy 3
│   ├── semantic.py           strategy 4
│   ├── embeddings.py         abstraction: get_embedder() -> .embed(text)
│   └── registry.py           catalog (label + explanation sentence + module)
├── management/commands/
│   ├── load_demo_articles.py   load fixtures + compute embeddings
│   └── search_report.py        print the strategy comparison (SEARCH_COMPARISON.md)
├── fixtures/demo_articles.json
└── templates/articles/       base.html, search.html, compare.html
```

Each module in `search/` exposes the same function:

```python
def search(query: str) -> list[SearchResult]: ...
```

If `query` is empty, the function returns **all** articles.

## Demo != production

This project favors readability. A real application would need at least: store
the `tsvector` and the vector in indexed columns (GIN, HNSW), re-sync embeddings
on `save()` or via a signal / background task, choose a relevance threshold,
measure performance on a realistic volume, and probably combine several
strategies (hybrid lexical + semantic search) rather than pick a single one.
