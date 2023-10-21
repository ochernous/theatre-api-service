from django.db import models


class TheatreHall(models.Model):
    name = models.CharField(max_length=128)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return self.name
