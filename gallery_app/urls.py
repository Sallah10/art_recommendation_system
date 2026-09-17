from django.urls import path, include
from . import views

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register("art_works", views.ArtWorks)
router.register('interactions', views.UserInteraction)

#urlpatterns = router.urls

urlpatterns = [
    path("", include(router.urls)),
    path("get_all", views.get_arts, name='all-arts'),
    path('api/recommendations/<int:user_id>/', views.recommend_artworks, name='recommendations'),
]



