# Generated by Django 3.0.2 on 2020-05-17 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cart', '0014_auto_20200515_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
        migrations.AddField(
            model_name='order',
            name='weight',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
    ]