# Generated by Django 3.1.7 on 2021-04-24 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0010_auto_20210424_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimages',
            name='image',
            field=models.ImageField(upload_to='uploads/product_imgs'),
        ),
    ]
