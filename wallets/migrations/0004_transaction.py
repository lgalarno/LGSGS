# Generated by Django 4.2.13 on 2024-06-25 01:58

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("assets", "0009_alter_asset_ticker_alter_asset_trader"),
        ("wallets", "0003_wallet_lastviewed_alter_transfer_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
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
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "quantity",
                    models.FloatField(
                        validators=[django.core.validators.MinValueValidator(0.0)]
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=6,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0.0)],
                    ),
                ),
                (
                    "fees",
                    models.DecimalField(
                        decimal_places=6,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0.0)],
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "ticker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ticker",
                        to="assets.ticker",
                    ),
                ),
                (
                    "trader",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trader",
                        to="assets.trader",
                    ),
                ),
                (
                    "wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="wallets.wallet"
                    ),
                ),
            ],
            options={
                "ordering": ["trader"],
            },
        ),
    ]
