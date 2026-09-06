# Search strategies — observed results

Real output from the demo dataset (26 articles, embeddings computed with
`all-MiniLM-L6-v2`). Regenerate with:

```bash
python manage.py search_report        # add --top N to change how many rows
```

Reading the tables:

- **count** = total rows the strategy returned (before the top-5 cut).
- Semantic always returns 15 (`TOP_K`, no relevance threshold) — the count is
  not a quality signal for that column.
- Trigram keeps everything above `similarity > 0.1`, so it also returns low-value
  rows.
- A score in parentheses is what the UI shows on the card.

---

## 1. Exact identifier — `ERR_CONNECTION_RESET`

| Strategy | Count | Top results |
|---|---|---|
| Contains | 1 | Debugging ERR_CONNECTION_RESET and dropped requests |
| Full Text | 1 | Debugging ERR_CONNECTION_RESET… `rank 1.0` |
| Trigram | 4 | Debugging ERR_CONNECTION_RESET… `0.43` · Connection pooling with PgBouncer `0.26` · Paginating large API responses `0.13` · Continuous integration… `0.11` |
| Semantic | 15 | Debugging ERR_CONNECTION_RESET… `0.56` · Connection pooling with PgBouncer `0.25` · **Writing unit tests for Django models `0.10`** · Designing a REST API… `0.10` · Running database migrations… `0.10` |

**Verdict:** Contains and Full Text are exact and clean. Trigram and Semantic
find it too but pad the list with unrelated rows and no threshold to cut them.
Weak differentiator — it mostly shows that Semantic is noisy on a symbol.

---

## 2. Precise technical term — `select_related`

| Strategy | Count | Top results |
|---|---|---|
| Contains | 1 | Optimizing Django database queries |
| Full Text | 1 | Optimizing Django database queries `rank 0.76` |
| Trigram | 1 | Optimizing Django database queries `0.23` |
| Semantic | 15 | Optimizing Django database queries `0.53` · Understanding the N+1 query problem `0.30` · Vector search and embeddings… `0.26` · Fuzzy search with pg_trgm… `0.19` · Full text search with PostgreSQL… `0.18` |

**Verdict:** the three lexical strategies pin the single correct article.
Semantic ranks it first but surrounds it with "database-ish" articles.

---

## 3. Several important words — `postgresql full text search`

| Strategy | Count | Top results |
|---|---|---|
| Contains | **0** | — (no field holds that exact substring) |
| Full Text | 2 | Full text search with PostgreSQL and Django `rank 1.0` · PostgreSQL indexing strategies `0.48` (its body says "full text search") |
| Trigram | 6 | Full text search with PostgreSQL… `0.64` · PostgreSQL indexing strategies `0.26` · Fuzzy search with pg_trgm… `0.19` · Scaling PostgreSQL… `0.18` · Connection pooling… `0.13` |
| Semantic | 15 | Full text search with PostgreSQL… `0.64` · Fuzzy search with pg_trgm… `0.51` · PostgreSQL indexing strategies `0.50` · Vector search and embeddings… `0.38` · Scaling PostgreSQL… `0.27` |

**Verdict:** Contains fails entirely (words not contiguous). Full Text ranks the
right article top and only adds a legitimately-related one. Trigram/Semantic
return a broader "PostgreSQL" cluster.

---

## 4. Words out of order + grammatical variant — `Django query optimization`

| Strategy | Count | Top results |
|---|---|---|
| Contains | **0** | — |
| Full Text | 1 | Optimizing Django database queries `rank 1.0` |
| Trigram | 9 | Optimizing Django database queries `0.43` · User authentication in Django `0.24` · Designing a REST API with Django `0.14` · Full text search… with Django `0.14` · Writing unit tests for Django models `0.13` |
| Semantic | 15 | Optimizing Django database queries `0.71` · Caching strategies for faster web pages `0.57` · Full text search with PostgreSQL… `0.49` · Designing a REST API with Django `0.41` · Deploying Django with Gunicorn… `0.40` |

**Verdict:** clean win for Full Text — `optimization`→`optim`, `query`→`queri`,
order ignored. Trigram latches onto the shared word "Django" and drifts.

---

## 5. Grammatical variant — `testing django models`

| Strategy | Count | Top results |
|---|---|---|
| Contains | **0** | — (the article says "tests", not "testing") |
| Full Text | 2 | Writing unit tests for Django models `rank 1.0` · Test fixtures and factories: pytest vs Django TestCase `0.92` |
| Trigram | 11 | Writing unit tests for Django models `0.55` · Designing a REST API with Django `0.23` · Optimizing Django database queries `0.19` · Test fixtures and factories… `0.18` · Deploying Django… `0.17` |
| Semantic | 15 | Writing unit tests for Django models `0.77` · Test fixtures and factories… `0.59` · Designing a REST API with Django `0.44` · User authentication in Django `0.41` · Deploying Django… `0.39` |

**Verdict:** Full Text and Semantic both surface the two test articles cleanly.
Contains misses on the `testing`/`tests` difference alone.

---

## 6. Typo — `autentication`

| Strategy | Count | Top results |
|---|---|---|
| Contains | **0** | — |
| Full Text | **0** | — (`autent` is not a lexeme of `authentication`) |
| Trigram | 3 | **User authentication in Django `0.38`** · Continuous integration for web applications `0.17` · Securing session cookies and CSRF tokens `0.15` |
| Semantic | 15 | User authentication in Django `0.22` · Securing session cookies and CSRF tokens `0.14` · Scaling PostgreSQL… `0.12` · Software architecture patterns… `0.11` · Reducing page load time… `0.11` |

**Verdict:** the clearest differentiator. Only Trigram recovers the intended
article with a usable score. Semantic technically ranks it first too, but at
`0.22` — barely above the noise.

---

## 7. Synonym / rephrasing — `make my website load faster`

| Strategy | Count | Top results |
|---|---|---|
| Contains | **0** | — |
| Full Text | **0** | — (`website` ≠ `site`, AND of 4 lexemes matches nothing) |
| Trigram | 2 | Caching strategies for faster web pages `0.18` · Reducing page load time and Core Web Vitals `0.13` |
| Semantic | 15 | **Reducing page load time and Core Web Vitals `0.71`** · Caching strategies for faster web pages `0.41` · Optimizing Django database queries `0.28` · Understanding the N+1 query problem `0.23` · Deploying Django… `0.22` |

**Verdict:** strong win for Semantic — it maps "website load faster" onto "page
load time / Core Web Vitals / caching" with a high score. Trigram only catches
the literal word "faster".

---

## 8. User intent, no shared keywords — `my Django application makes too many SQL queries`

| Strategy | Count | Top results |
|---|---|---|
| Contains | **0** | — |
| Full Text | **0** | — (AND of 6+ lexemes; no article has them all) |
| Trigram | 14 | Optimizing Django database queries `0.23` · User authentication in Django `0.23` · Continuous integration… `0.16` · Full text search… `0.16` · Test fixtures… `0.15` |
| Semantic | 15 | **Optimizing Django database queries `0.67`** · Caching strategies for faster web pages `0.48` · Writing unit tests for Django models `0.47` · Full text search with PostgreSQL… `0.45` · Designing a REST API with Django `0.41` |

**Verdict:** Semantic is the only strategy that puts a genuinely useful article
first (the `select_related` / N+1 one). Note it is not perfect: "Understanding
the N+1 query problem" itself lands outside the top 5, behind some noise. Trigram
scores the string against short titles and returns near-random low matches.

---

## 9. Common word, ranking matters — `authentication`

| Strategy | Count | Top results |
|---|---|---|
| Contains | 2 | Securing session cookies and CSRF tokens · User authentication in Django  *(order = title A→Z, not relevance)* |
| Full Text | 2 | **User authentication in Django `rank 0.68`** · Securing session cookies and CSRF tokens `0.27` |
| Trigram | 3 | User authentication in Django `0.50` · Securing session cookies and CSRF tokens `0.19` · Continuous integration… `0.17` |
| Semantic | 15 | User authentication in Django `0.53` · Securing session cookies and CSRF tokens `0.42` · Password hashing and credential storage `0.39` · Structured logging… `0.19` · Designing a REST API… `0.10` |

**Verdict:** all four find the right articles, but only Full Text / Trigram /
Semantic **rank** the title match first. Contains returns the same set in
alphabetical order — it has no notion of relevance. Semantic also pulls in
"Password hashing and credential storage" (no shared word, related meaning).

---

## Synthesis matrix

Legend: ✅✅ clearly best · ✅ works well · ⚠️ partial / noisy / threshold-dependent · ❌ fails

| Query type | Contains | Full Text | Trigram | Semantic |
|---|---|---|---|---|
| exact identifier (`ERR_CONNECTION_RESET`) | ✅✅ | ✅✅ | ⚠️ (+3 noise) | ⚠️ (+13 noise) |
| precise term (`select_related`) | ✅✅ | ✅✅ | ✅ | ⚠️ (diluted) |
| several words (`postgresql full text search`) | ❌ | ✅✅ | ⚠️ | ✅ |
| words out of order + grammar (`Django query optimization`) | ❌ | ✅✅ | ⚠️ | ✅ |
| grammatical variant (`testing` vs `tests`) | ❌ | ✅✅ | ⚠️ | ✅✅ |
| typo (`autentication`) | ❌ | ❌ | ✅✅ | ⚠️ (low score) |
| synonym / rephrasing (`make my website load faster`) | ❌ | ❌ | ⚠️ | ✅✅ |
| user intent, no keywords (`too many SQL queries`) | ❌ | ❌ | ❌ | ✅✅ |
| common word, ranking (`authentication`) | ⚠️ (no ranking) | ✅✅ | ✅ | ✅ |

## Takeaways

- **Contains** is perfect for an exact substring or identifier and useless for
  everything else — no reordering, no stemming, no ranking.
- **Full Text** is the best all-rounder for keyword search: stemming, word-order
  independence, real relevance ranking with field weighting. It cannot cross the
  vocabulary gap (`website` vs `site`) and does not fix typos.
- **Trigram** earns its place on exactly one axis: typo tolerance. Its low
  threshold makes every other query noisy; it should be a fallback, not a
  primary engine.
- **Semantic** is the only strategy that answers a rephrasing or an intent with
  no shared words. But it always returns `TOP_K` rows, its scores are not
  calibrated (a real hit at `0.22` on the typo query, noise at `0.10`), and it
  is the weakest on precise identifiers.

No strategy wins across the board. In practice you would combine Full Text (for
keywords, with ranking) and Semantic (for intent), and keep Trigram as a
typo-tolerant fallback — a **hybrid** search, not a single engine.
