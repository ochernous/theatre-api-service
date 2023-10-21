from django.db import models


class TheatreHall(models.Model):
    name = models.CharField(max_length=127)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return self.name


class Play(models.Model):
    title = models.CharField(max_length=127)
    description = models.TextField()
    actors = models.ManyToManyField(Actor, related_name="plays")
    genres = models.ManyToManyField(Genre, related_name="plays")

    def __str__(self):
        return self.title


class Performance(models.Model):
    show_time = models.DateTimeField()
    play = models.ForeignKey(Play, on_delete=models.CASCADE)
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.play.title} {self.show_time}"
