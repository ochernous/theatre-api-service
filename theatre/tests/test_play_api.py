from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, Genre, Actor
from theatre.serializers import PlayListSerializer, PlayDetailSerializer

PLAY_URL = reverse("theatre:play-list")


def sample_play(**params):
    defaults = {
        "title": "Sample play",
        "description": "Sample description",
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": "Drama",
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)


def sample_actor(**params):
    defaults = {"first_name": "John", "last_name": "Smith"}
    defaults.update(params)

    return Actor.objects.create(**defaults)

def detail_url(play_id):
    return reverse("theatre:play-detail", args=[play_id])


class AuthenticatedOrUnauthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="1password2"
        )
        self.client.force_authenticate(self.user)
        self.play1 = sample_play(title="Hamlet")
        self.play2 = sample_play(title="Hamlet 2")
        self.play3 = sample_play(title="Phantom")
        self.genre1 = sample_genre(name="genre1")
        self.genre2 = sample_genre(name="genre2")
        self.actor1 = sample_actor(first_name="John", last_name="Smith")
        self.actor2 = sample_actor(first_name="Alice", last_name="Black")

    def test_list_plays(self):
        self.play1.genres.add(self.genre1, self.genre2)
        response = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_plays_by_genres(self):
        self.play1.genres.add(self.genre1)
        self.play2.genres.add(self.genre2)
        response = self.client.get(PLAY_URL, {
            "genres": f"{self.genre1.id},{self.genre2.id}"}
                                   )

        serializer1 = PlayListSerializer(self.play1)
        serializer2 = PlayListSerializer(self.play2)
        serializer3 = PlayListSerializer(self.play3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_filter_plays_by_actors(self):
        self.play1.actors.add(self.actor1)
        self.play2.actors.add(self.actor2)
        response = self.client.get(PLAY_URL, {
            "actors": f"{self.actor1.id},{self.actor2.id}"}
                                   )

        serializer1 = PlayListSerializer(self.play1)
        serializer2 = PlayListSerializer(self.play2)
        serializer3 = PlayListSerializer(self.play3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_filter_plays_by_title(self):
        response = self.client.get(PLAY_URL, {"title": "Hamlet"})

        serializer1 = PlayListSerializer(self.play1)
        serializer2 = PlayListSerializer(self.play2)
        serializer3 = PlayListSerializer(self.play3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_retrieve_play_detail(self):
        self.play1.genres.add(self.genre1)
        url = detail_url(self.play1.id)
        response = self.client.get(url)

        serializer = PlayDetailSerializer(self.play1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_play_forbidden(self):
        payload = {
            "title": "Test",
            "description": "play about tests",
        }

        response = self.client.post(PLAY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="1pass5word4",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
        self.genre1 = sample_genre(name="genre1")
        self.genre2 = sample_genre(name="genre2")
        self.actor1 = sample_actor(first_name="John", last_name="Smith")
        self.actor2 = sample_actor(first_name="Alice", last_name="Black")

    def test_create_play(self):
        actors_ids = [self.actor1.id, self.actor2.id]
        genres_ids = [self.genre1.id, self.genre2.id]

        payload = {
            "title": "Test",
            "description": "play about tests",
            "actors": actors_ids,
            "genres": genres_ids
        }

        response = self.client.post(PLAY_URL, payload)
        play = Play.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            if key in ["actors", "genres"]:
                self.assertCountEqual(payload[key], getattr(play, key).values_list('id', flat=True))
            else:
                self.assertEqual(payload[key], getattr(play, key))

    def test_create_play_with_genres_and_actors(self):
        payload = {
            "title": "Test",
            "description": "play about tests",
            "genres": [self.genre1.id, self.genre2.id],
            "actors": [self.actor1.id, self.actor2.id]
        }

        response = self.client.post(PLAY_URL, payload)
        play = Play.objects.get(id=response.data["id"])
        genres = Genre.objects.all()
        actors = Actor.objects.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(genres.count(), 2)
        self.assertEqual(actors.count(), 2)
        self.assertIn(self.genre1, genres)
        self.assertIn(self.genre2, genres)
        self.assertIn(self.actor1, actors)
        self.assertIn(self.actor2, actors)

        for key in payload:
            if key in ["actors", "genres"]:
                self.assertCountEqual(payload[key], getattr(play, key).values_list('id', flat=True))
            else:
                self.assertEqual(payload[key], getattr(play, key))

    def test_delete_play_not_allowed(self):
        play = sample_play()
        url = detail_url(play.id)
        response = self.client.delete(url)

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
