# Generated by Django 3.1.3 on 2020-12-06 07:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('airpark_app', '0002_auto_20201206_0510'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='stripe_customer_id',
        ),
    ]