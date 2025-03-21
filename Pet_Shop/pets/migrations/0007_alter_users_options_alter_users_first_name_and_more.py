# Generated by Django 5.1.5 on 2025-02-17 13:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("pets", "0006_product_alter_orders_status"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="users",
            options={},
        ),
        migrations.AlterField(
            model_name="users",
            name="first_name",
            field=models.CharField(max_length=100),
        ),
        migrations.AddIndex(
            model_name="items",
            index=models.Index(fields=["title"], name="pets_items_title_3df109_idx"),
        ),
        migrations.AddIndex(
            model_name="users",
            index=models.Index(fields=["email"], name="pets_users_email_3c13f8_idx"),
        ),
    ]
