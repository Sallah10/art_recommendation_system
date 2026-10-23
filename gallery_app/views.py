import re

from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Art_Work, Collection, UserInteraction
from .recommendations import (
    interaction_map_for_session,
    recommend_for_session,
    similar_artworks,
    taste_profile,
)
from .serializers import (
    ArtWorkSerializer,
    CollectionSerializer,
    RecommendedArtWorkSerializer,
    UserInteractionSerializer,
)

SESSION_HEADER = "HTTP_X_SESSION_ID"
SESSION_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def get_session_key(request, allow_query=True):
    raw = request.META.get(SESSION_HEADER, "")
    if not raw and allow_query:
        raw = request.query_params.get("session_id", "")
    raw = (raw or "").strip()
    if SESSION_PATTERN.match(raw):
        return raw
    return ""


def annotated_artworks():
    return Art_Work.objects.annotate(
        likes=Count("interactions", filter=Q(interactions__liked=True)),
        bookmarks=Count("interactions", filter=Q(interactions__bookmarked=True)),
        views=Sum("interactions__view_count"),
    )


class ArtWorkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ArtWorkSerializer
    lookup_field = "pk"

    def get_queryset(self):
        queryset = annotated_artworks()
        params = self.request.query_params

        style = params.get("style")
        if style:
            queryset = queryset.filter(style__iexact=style)

        era = params.get("era")
        if era:
            queryset = queryset.filter(era__iexact=era)

        artist = params.get("artist")
        if artist:
            queryset = queryset.filter(artiste__icontains=artist)

        collection = params.get("collection")
        if collection:
            queryset = queryset.filter(collections__slug=collection)

        if params.get("featured") in ("1", "true", "yes"):
            queryset = queryset.filter(featured=True)

        search = params.get("search")
        if search:
            queryset = queryset.filter(
                Q(art_title__icontains=search)
                | Q(artiste__icontains=search)
                | Q(style__icontains=search)
                | Q(era__icontains=search)
                | Q(art_desc__icontains=search)
            )

        ordering = params.get("ordering", "art_title")
        allowed = {
            "art_title",
            "-art_title",
            "likes",
            "-likes",
            "bookmarks",
            "-bookmarks",
            "views",
            "-views",
            "created_at",
            "-created_at",
        }
        if ordering in allowed:
            queryset = queryset.order_by(ordering, "art_title")

        return queryset.distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["interactions"] = interaction_map_for_session(
            get_session_key(self.request)
        )
        return context

    @action(detail=True, methods=["get"])
    def similar(self, request, pk=None):
        artwork = self.get_object()
        neighbours = similar_artworks(artwork, limit=4)
        serializer = self.get_serializer(neighbours, many=True)
        return Response(serializer.data)


class CollectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CollectionSerializer
    lookup_field = "slug"
    pagination_class = None

    def get_queryset(self):
        return Collection.objects.annotate(
            artwork_count=Count("artworks")
        ).prefetch_related("artworks")


class InteractionView(APIView):
    """Toggle a like/bookmark or record a view for the current session."""

    def get(self, request):
        session_key = get_session_key(request)
        if not session_key:
            return Response({"detail": "A valid session id is required."}, status=400)
        rows = (
            UserInteraction.objects.filter(session_key=session_key)
            .select_related("artwork")
            .order_by("-last_interacted")
        )
        return Response(UserInteractionSerializer(rows, many=True).data)

    def post(self, request):
        session_key = get_session_key(request)
        if not session_key:
            return Response({"detail": "A valid session id is required."}, status=400)

        artwork_id = request.data.get("artwork") or request.data.get("artworkId")
        interaction_type = (request.data.get("type") or request.data.get("interactionType") or "").lower()
        artwork = get_object_or_404(Art_Work, pk=artwork_id)

        if interaction_type not in ("like", "bookmark", "view"):
            return Response(
                {"detail": "type must be one of: like, bookmark, view."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            interaction, _ = UserInteraction.objects.get_or_create(
                session_key=session_key,
                artwork=artwork,
                defaults={"user": request.user if request.user.is_authenticated else None},
            )
            if interaction_type == "like":
                interaction.liked = not interaction.liked
            elif interaction_type == "bookmark":
                interaction.bookmarked = not interaction.bookmarked
            else:
                interaction.view_count += 1
            interaction.save()

        counts = Art_Work.objects.filter(pk=artwork.id).annotate(
            likes=Count("interactions", filter=Q(interactions__liked=True)),
            bookmarks=Count("interactions", filter=Q(interactions__bookmarked=True)),
            views=Sum("interactions__view_count"),
        ).first()

        return Response(
            {
                "artwork": artwork.id,
                "liked": interaction.liked,
                "bookmarked": interaction.bookmarked,
                "view_count": interaction.view_count,
                "likes": counts.likes,
                "bookmarks": counts.bookmarks,
                "views": counts.views or 0,
            }
        )


class RecommendationView(APIView):
    def post(self, request):
        session_key = get_session_key(request)
        try:
            limit = min(int(request.data.get("limit", 8)), 24)
        except (TypeError, ValueError):
            limit = 8

        ranked = recommend_for_session(session_key, limit=limit) if session_key else []
        if not ranked:
            ranked = [
                {"artwork": artwork, "score": 0.0, "reason": "Start with a curator's pick"}
                for artwork in annotated_artworks().order_by("-featured", "-created_at")[:limit]
            ]

        serializer = RecommendedArtWorkSerializer(
            ranked,
            many=True,
            context={
                "request": request,
                "interactions": interaction_map_for_session(session_key),
            },
        )
        return Response({"results": serializer.data, "personalised": bool(session_key)})


class TasteProfileView(APIView):
    def get(self, request):
        session_key = get_session_key(request)
        if not session_key:
            return Response({"signals": 0, "top_styles": [], "top_eras": []})
        return Response(taste_profile(session_key))


class StatsView(APIView):
    def get(self, request):
        return Response(
            {
                "artworks": Art_Work.objects.count(),
                "collections": Collection.objects.count(),
                "styles": Art_Work.objects.exclude(style="").values("style").distinct().count(),
                "interactions": UserInteraction.objects.count(),
            }
        )


class FacetsView(APIView):
    """Available filters for the gallery, with counts."""

    def get(self, request):
        styles = (
            Art_Work.objects.exclude(style="")
            .values("style")
            .annotate(count=Count("id"))
            .order_by("-count", "style")
        )
        eras = (
            Art_Work.objects.exclude(era="")
            .values("era")
            .annotate(count=Count("id"))
            .order_by("-count", "era")
        )
        return Response(
            {
                "styles": list(styles),
                "eras": list(eras),
                "total": Art_Work.objects.count(),
            }
        )


@api_view(["GET"])
def health(request):
    return Response({"status": "ok", "service": "escurator-api"})
