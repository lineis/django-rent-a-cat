# Generated by Django 2.2.14 on 2023-01-04 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20230104_2320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='reviews',
            field=models.TextField(default=''),
        ),
    ]
