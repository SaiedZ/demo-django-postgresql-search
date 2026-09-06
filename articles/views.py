"""Thin views: pick a strategy from articles/search/ and render it. No search
logic lives here."""

from django.shortcuts import render

from .search.registry import COMPARE_ORDER, DEFAULT_STRATEGY, STRATEGIES

COMPARE_LIMIT = 5


def search_view(request):
    query = request.GET.get("q", "").strip()
    strategy_key = request.GET.get("strategy", DEFAULT_STRATEGY)
    if strategy_key not in STRATEGIES:
        strategy_key = DEFAULT_STRATEGY

    strategy = STRATEGIES[strategy_key]
    results = strategy["module"].search(query)

    context = {
        "query": query,
        "strategy_key": strategy_key,
        "strategy": strategy,
        "strategies": STRATEGIES,
        "results": results,
        "result_count": len(results),
    }
    return render(request, "articles/search.html", context)


def compare_view(request):
    query = request.GET.get("q", "").strip()

    blocks = []
    for key in COMPARE_ORDER:
        strategy = STRATEGIES[key]
        results = strategy["module"].search(query) if query else []
        blocks.append(
            {
                "key": key,
                "label": strategy["label"],
                "description": strategy["description"],
                "results": results[:COMPARE_LIMIT],
                "total": len(results),
            }
        )

    return render(request, "articles/compare.html", {"query": query, "blocks": blocks})
