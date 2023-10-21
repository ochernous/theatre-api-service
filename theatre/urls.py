from django.urls import path, include
from rest_framework import routers

from theatre.views import TheatreHallViewSet, ActorViewSet, GenreViewSet

router = routers.DefaultRouter()
router.register("theatre_halls", TheatreHallViewSet)
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "theatre"
