# Generated by Django 3.2.12 on 2023-06-01 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0019_recommendedproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recommendedproduct',
            name='product_name',
            field=models.CharField(max_length=255),
        ),
    ]
