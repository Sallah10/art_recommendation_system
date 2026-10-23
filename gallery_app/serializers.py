from rest_framework import serializers

from .models import Art_Work, Collection, UserInteraction


class ArtWorkSerializer(serializers.ModelSerializer):
    art_image = serializers.SerializerMethodField()
    tags = serializers.ReadOnlyField()
    likes = serializers.IntegerField(read_only=True, default=0)
    bookmarks = serializers.IntegerField(read_only=True, default=0)
    views = serializers.IntegerField(read_only=True, default=0)
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Art_Work
        fields = (
            "id",
            "art_title",
            "artiste",
            "art_desc",
            "art_image",
            "style",
            "era",
            "medium",
            "year",
            "featured",
            "tags",
            "likes",
            "bookmarks",
            "views",
            "is_liked",
            "is_bookmarked",
        )

    def get_art_image(self, obj):
        if not obj.art_image:
            return None
        request = self.context.get("request")
        url = obj.art_image.url
        return request.build_absolute_uri(url) if request else url

    def _interaction(self, obj):
        return self.context.get("interactions", {}).get(obj.id, {})

    def get_is_liked(self, obj):
        return bool(self._interaction(obj).get("liked"))

    def get_is_bookmarked(self, obj):
        return bool(self._interaction(obj).get("bookmarked"))


class RecommendedArtWorkSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    art_title = serializers.CharField()
    artiste = serializers.CharField()
    art_desc = serializers.CharField()
    art_image = serializers.SerializerMethodField()
    style = serializers.CharField(allow_blank=True)
    era = serializers.CharField(allow_blank=True)
    medium = serializers.CharField(allow_blank=True)
    year = serializers.CharField(allow_blank=True)
    featured = serializers.BooleanField()
    tags = serializers.ReadOnlyField()
    likes = serializers.IntegerField()
    bookmarks = serializers.IntegerField()
    views = serializers.IntegerField(allow_null=True)
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    reason = serializers.CharField()
    score = serializers.FloatField()

    def get_art_image(self, obj):
        if isinstance(obj, dict):
            artwork = obj.get("artwork")
            image = getattr(artwork, "art_image", None)
        else:
            image = getattr(obj, "art_image", None) or getattr(getattr(obj, "artwork", None), "art_image", None)
        if image and hasattr(image, "url"):
            request = self.context.get("request")
            url = image.url
            return request.build_absolute_uri(url) if request else url
        if isinstance(obj, dict) and obj.get("artwork"):
            artwork = obj["artwork"]
            if artwork.art_image and hasattr(artwork.art_image, "url"):
                request = self.context.get("request")
                url = artwork.art_image.url
                return request.build_absolute_uri(url) if request else url
        return None

    def _interaction(self, obj):
        interactions = self.context.get("interactions", {})
        if isinstance(obj, dict):
            artwork = obj.get("artwork")
            if artwork and hasattr(artwork, "id"):
                return interactions.get(artwork.id, {})
            return interactions.get(obj.get("id"), {})
        return interactions.get(getattr(obj, "id"), {})

    def get_is_liked(self, obj):
        return bool(self._interaction(obj).get("liked"))

    def get_is_bookmarked(self, obj):
        return bool(self._interaction(obj).get("bookmarked"))

    def to_representation(self, instance):
        if isinstance(instance, dict):
            artwork = instance["artwork"]
            views = getattr(artwork, "views", None)
            if views is None:
                views = 0
            data = {
                "id": artwork.id,
                "art_title": artwork.art_title,
                "artiste": artwork.artiste,
                "art_desc": artwork.art_desc,
                "art_image": artwork.art_image,
                "style": artwork.style,
                "era": artwork.era,
                "medium": artwork.medium,
                "year": artwork.year,
                "featured": artwork.featured,
                "tags": artwork.tags,
                "likes": getattr(artwork, "likes", 0) or 0,
                "bookmarks": getattr(artwork, "bookmarks", 0) or 0,
                "views": views or 0,
                "reason": instance.get("reason", ""),
                "score": instance.get("score", 0.0),
            }
            return super().to_representation(data)
        return super().to_representation(instance)


class CollectionSerializer(serializers.ModelSerializer):
    artwork_count = serializers.IntegerField(read_only=True)
    cover = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "accent",
            "featured",
            "artwork_count",
            "cover",
            "tags",
        )

    def get_cover(self, obj):
        artwork = next(iter(obj.artworks.all()), None)
        if artwork is None or not artwork.art_image:
            return None
        request = self.context.get("request")
        url = artwork.art_image.url
        return request.build_absolute_uri(url) if request else url

    def get_tags(self, obj):
        tags = {}
        for artwork in obj.artworks.all():
            for tag in artwork.tags:
                tags[tag] = tags.get(tag, 0) + 1
        return [tag for tag, _ in sorted(tags.items(), key=lambda item: -item[1])][:4]


class UserInteractionSerializer(serializers.ModelSerializer):
    artwork = ArtWorkSerializer(read_only=True)
    artwork_id = serializers.PrimaryKeyRelatedField(
        queryset=Art_Work.objects.all(), source="artwork", write_only=True
    )

    class Meta:
        model = UserInteraction
        fields = (
            "id",
            "artwork",
            "artwork_id",
            "liked",
            "bookmarked",
            "view_count",
            "last_interacted",
        )
        read_only_fields = ("id", "last_interacted", "view_count")
