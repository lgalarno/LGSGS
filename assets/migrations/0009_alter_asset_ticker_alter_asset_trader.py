# Generated by Django 4.2.13 on 2024-06-25 01:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("assets", "0008_ticker_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="ticker",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="asset",
                to="assets.ticker",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="trader",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="asset",
                to="assets.trader",
            ),
        ),
    ]
