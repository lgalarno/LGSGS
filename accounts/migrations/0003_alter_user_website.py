# Generated by Django 4.2.13 on 2024-06-22 05:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_user_website"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="website",
            field=models.URLField(blank=True, verbose_name="External portfolio url"),
        ),
    ]