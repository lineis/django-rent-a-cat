# Generated by Django 2.2.14 on 2022-12-15 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_item_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='gender',
            field=models.CharField(choices=[('M', 'Boy'), ('F', 'Girl')], default='M', max_length=1),
        ),
    ]