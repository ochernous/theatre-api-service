from django.urls import path, include
from rest_framework import routers

from theatre.views import TheatreHallViewSet, ActorViewSet

router = routers.DefaultRouter()
router.register("theatre_halls", TheatreHallViewSet)
router.register("actors", ActorViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "theatre"
