from django.contrib import admin

from .models import Art_Work, Collection, UserInteraction


@admin.register(Art_Work)
class ArtWorkAdmin(admin.ModelAdmin):
    list_display = ("art_title", "artiste", "style", "era", "featured")
    list_filter = ("style", "era", "featured")
    search_fields = ("art_title", "artiste", "art_desc")
    list_editable = ("featured",)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "featured")
    list_filter = ("featured",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("artworks",)


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ("session_key", "artwork", "liked", "bookmarked", "view_count")
    list_filter = ("liked", "bookmarked")
    search_fields = ("session_key", "artwork__art_title")
    raw_id_fields = ("artwork",)
