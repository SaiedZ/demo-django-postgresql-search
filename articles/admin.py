from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "has_embedding")
    search_fields = ("title", "description", "content")

    @admin.display(boolean=True, description="embedding")
    def has_embedding(self, obj):
        return obj.embedding is not None
