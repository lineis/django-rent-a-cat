# Generated by Django 2.2.14 on 2023-01-04 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_item_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='rental_duration',
            field=models.FloatField(default=1.0),
        ),
    ]
