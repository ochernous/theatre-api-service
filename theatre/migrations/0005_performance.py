# Generated by Django 4.2.6 on 2023-10-21 22:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("theatre", "0004_play"),
    ]

    operations = [
        migrations.CreateModel(
            name="Performance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("show_time", models.DateTimeField()),
                (
                    "play",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="theatre.play"
                    ),
                ),
                (
                    "theatre_hall",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="theatre.theatrehall",
                    ),
                ),
            ],
        ),
    ]
