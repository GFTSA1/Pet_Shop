# Generated by Django 5.1.5 on 2025-02-07 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0005_alter_orders_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
