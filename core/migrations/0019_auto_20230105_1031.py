# Generated by Django 2.2.14 on 2023-01-05 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20230105_0024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='rental_duration',
            field=models.IntegerField(),
        ),
    ]