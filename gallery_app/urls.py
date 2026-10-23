from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("art_works", views.ArtWorkViewSet, basename="artwork")
router.register("collections", views.CollectionViewSet, basename="collection")

urlpatterns = [
    path("", include(router.urls)),
    path("interactions/", views.InteractionView.as_view(), name="interactions"),
    path("recommendations/", views.RecommendationView.as_view(), name="recommendations"),
    path("taste/", views.TasteProfileView.as_view(), name="taste"),
    path("stats/", views.StatsView.as_view(), name="stats"),
    path("facets/", views.FacetsView.as_view(), name="facets"),
    path("health/", views.health, name="health"),
]
