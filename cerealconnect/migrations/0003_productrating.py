# Generated by Django 5.0.2 on 2024-12-09 17:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cerealconnect", "0002_contactmessage"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductRating",
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
                (
                    "rating",
                    models.PositiveIntegerField(
                        choices=[
                            (1, "1 Star"),
                            (2, "2 Stars"),
                            (3, "3 Stars"),
                            (4, "4 Stars"),
                            (5, "5 Stars"),
                        ]
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_ratings",
                        to="cerealconnect.product",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_ratings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("product", "user")},
            },
        ),
    ]