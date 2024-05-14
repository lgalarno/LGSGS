# Generated by Django 4.2.13 on 2024-05-12 02:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assets", "0002_asset_monitor"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="emailed",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="asset",
            name="monitor",
            field=models.BooleanField(default=True),
        ),
    ]