# Generated by Django 5.1.5 on 2025-02-05 17:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pets", "0004_alter_itemsorders_order_id_alter_orders_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orders",
            name="status",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending"),
                    ("Awaiting", "Awaiting"),
                    ("Shipped", "Shipped"),
                    ("Completed", "Completed"),
                    ("Canceled", "Canceled"),
                ]
            ),
        ),
    ]
