from datetime import datetime

from django.db.models import F, Count
from rest_framework import viewsets

from theatre.models import (
    TheatreHall,
    Actor,
    Genre,
    Play,
    Performance,
    Reservation,
    Ticket,
)

from theatre.serializers import (
    TheatreHallSerializer,
    ActorSerializer,
    GenreSerializer,
    PlaySerializer,
    PerformanceSerializer,
    ReservationSerializer,
    TicketSerializer,
    PerformanceListSerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    PerformanceDetailSerializer,
    ReservationListSerializer,
)


class ParamsToIntMixin:
    @staticmethod
    def params_to_int(qs) -> list:
        return [int(str_id) for str_id in qs.split(",")]


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class PlayViewSet(ParamsToIntMixin, viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def get_queryset(self):
        queryset = self.queryset.prefetch_related("actors", "genres")
        actors = self.request.query_params.get("actors", "")
        genres = self.request.query_params.get("genres", "")
        title = self.request.query_params.get("title", "")

        if actors:
            actors_ids = self.params_to_int(actors)
            queryset = queryset.filter(actors__id__in=actors_ids)

        if genres:
            genres_ids = self.params_to_int(genres)
            queryset = queryset.filter(genres__id__in=genres_ids)

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        return self.serializer_class


class PerformanceViewSet(ParamsToIntMixin, viewsets.ModelViewSet):
    queryset = (
        Performance.objects.all()
        .select_related("theatre_hall", "play")
        .annotate(
            tickets_available=(
                F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                - Count("tickets")
            )
        ).order_by("show_time")
    )
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset
        plays = self.request.query_params.get("plays", "")
        date = self.request.query_params.get("date", "")

        if plays:
            plays_ids = self.params_to_int(plays)
            queryset = queryset.filter(play__id__in=plays_ids)

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer

        if self.action == "retrieve":
            return PerformanceDetailSerializer

        return self.serializer_class


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__performance__theatre_hall", "tickets__performance__play")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
