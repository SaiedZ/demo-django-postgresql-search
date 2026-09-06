"""python manage.py search_report

Runs a fixed set of queries through the four strategies and prints the top
results with their scores. Used to regenerate SEARCH_COMPARISON.md.
"""

from django.core.management.base import BaseCommand

from articles.search.registry import COMPARE_ORDER, STRATEGIES

QUERIES = [
    ("exact identifier", "ERR_CONNECTION_RESET"),
    ("precise technical term", "select_related"),
    ("several important words", "postgresql full text search"),
    ("words out of order + grammar", "Django query optimization"),
    ("grammatical variant", "testing django models"),
    ("typo", "autentication"),
    ("synonym / rephrasing", "make my website load faster"),
    ("user intent, no keywords", "my Django application makes too many SQL queries"),
    ("common word (ranking)", "authentication"),
]


class Command(BaseCommand):
    help = "Print a comparison report of the four search strategies."

    def add_arguments(self, parser):
        parser.add_argument("--top", type=int, default=5)

    def handle(self, *args, **options):
        top = options["top"]
        for label, query in QUERIES:
            self.stdout.write("=" * 90)
            self.stdout.write(f"{label}  |  query: {query!r}")
            self.stdout.write("=" * 90)
            for key in COMPARE_ORDER:
                results = STRATEGIES[key]["module"].search(query)
                self.stdout.write(
                    f"  [{STRATEGIES[key]['label']}]  {len(results)} result(s)"
                )
                for r in results[:top]:
                    score = "" if r.score is None else f"  ({r.score_label}: {r.score})"
                    self.stdout.write(f"      - {r.article.title}{score}")
                self.stdout.write("")
