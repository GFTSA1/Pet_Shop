# Generated by Django 5.1.5 on 2025-01-22 11:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pets", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="users",
            managers=[],
        ),
        migrations.RemoveField(
            model_name="users",
            name="username",
        ),
    ]
