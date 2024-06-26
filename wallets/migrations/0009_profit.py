# Generated by Django 4.2.13 on 2024-06-27 21:42

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("wallets", "0008_transaction_type_alter_transaction_currency"),
    ]

    operations = [
        migrations.CreateModel(
            name="Profit",
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
                    "profit",
                    models.DecimalField(
                        decimal_places=6,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0.0)],
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "transaction_bought",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bought",
                        to="wallets.transaction",
                    ),
                ),
                (
                    "transaction_sold",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sold",
                        to="wallets.transaction",
                    ),
                ),
            ],
        ),
    ]
