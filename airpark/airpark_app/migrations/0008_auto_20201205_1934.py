# Generated by Django 3.1.3 on 2020-12-05 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airpark_app', '0007_auto_20201205_0551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='discount_percent',
            field=models.CharField(default='', max_length=30),
        ),
    ]