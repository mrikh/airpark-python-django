# Generated by Django 3.1.2 on 2020-12-04 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airpark_app', '0005_carpark_airport_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='carpark',
            name='is_long_term',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]