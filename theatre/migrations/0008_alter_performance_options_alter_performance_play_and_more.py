# Generated by Django 4.2.6 on 2023-10-22 12:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("theatre", "0007_ticket"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="performance",
            options={"ordering": ["show_time"]},
        ),
        migrations.AlterField(
            model_name="performance",
            name="play",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="performances",
                to="theatre.play",
            ),
        ),
        migrations.AlterField(
            model_name="performance",
            name="theatre_hall",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="performances",
                to="theatre.theatrehall",
            ),
        ),
        migrations.AlterField(
            model_name="reservation",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reservations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
