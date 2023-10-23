# Generated by Django 4.2.6 on 2023-10-23 16:52

from django.db import migrations, models
import theatre.models


class Migration(migrations.Migration):
    dependencies = [
        ("theatre", "0009_alter_play_options_alter_genre_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="play",
            name="image",
            field=models.ImageField(
                null=True, upload_to=theatre.models.play_image_to_path
            ),
        ),
    ]