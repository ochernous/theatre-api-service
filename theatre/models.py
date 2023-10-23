import os.path
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class TheatreHall(models.Model):
    name = models.CharField(max_length=127)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Genre(models.Model):
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name


def play_image_to_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}.{extension}"

    return os.path.join("upload/plays/", filename)


class Play(models.Model):
    title = models.CharField(max_length=127)
    description = models.TextField()
    actors = models.ManyToManyField(Actor, related_name="plays")
    genres = models.ManyToManyField(Genre, related_name="plays")
    image = models.ImageField(null=True, upload_to=play_image_to_path)

    class Meta:
        ordering = ["title", ]

    def __str__(self):
        return self.title


class Performance(models.Model):
    show_time = models.DateTimeField()
    play = models.ForeignKey(Play, on_delete=models.CASCADE, related_name="performances")
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.CASCADE, related_name="performances")

    def __str__(self):
        return f"{self.play.title} {self.show_time}"

    class Meta:
        ordering = ["show_time", ]


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE, related_name="tickets")
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        unique_together = ("performance", "row", "seat")
        ordering = ["row", "seat"]

    @staticmethod
    def validate_seat_and_row(seat: int, row: int, performance, error_to_raise):
        for ticket_attr_value, ticket_attr_name, theatre_hall_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row")
        ]:
            count_attrs = getattr(performance.theatre_hall, theatre_hall_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} number must be in available range: (1, {theatre_hall_attr_name}): (1, {count_attrs})"
                    }
                )

    def clean(self):
        self.validate_seat_and_row(self.seat, self.row, self.performance, ValidationError)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        super(Ticket, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.performance} (row: {self.row}, seat: {self.seat})"
