# Generated by Django 5.1.6 on 2025-02-14 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0003_rename_place_destination'),
    ]

    operations = [
        migrations.AddField(
            model_name='destination',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='destination',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
