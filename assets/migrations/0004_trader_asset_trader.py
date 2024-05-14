# Generated by Django 4.2.13 on 2024-05-13 19:10

import assets.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("assets", "0003_asset_emailed_alter_asset_monitor"),
    ]

    operations = [
        migrations.CreateModel(
            name="Trader",
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
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "logo",
                    models.ImageField(
                        blank=True, null=True, upload_to=assets.models.upload_location
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="asset",
            name="trader",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="trader",
                to="assets.trader",
            ),
        ),
    ]
