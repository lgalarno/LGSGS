# Generated by Django 4.2.13 on 2024-05-21 23:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="website",
            field=models.URLField(blank=True),
        ),
    ]
