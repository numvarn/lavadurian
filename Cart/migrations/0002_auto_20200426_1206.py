# Generated by Django 3.0.2 on 2020-04-26 05:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Cart', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='chart',
            new_name='cart',
        ),
    ]