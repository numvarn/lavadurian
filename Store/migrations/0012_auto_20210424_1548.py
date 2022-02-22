# Generated by Django 3.1.7 on 2021-04-24 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0011_auto_20210424_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storecertificate',
            name='commercial_regis',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/certificates'),
        ),
        migrations.AlterField(
            model_name='storecertificate',
            name='food_storage_license',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/certificates'),
        ),
        migrations.AlterField(
            model_name='storecertificate',
            name='gmp_regis',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/certificates'),
        ),
        migrations.AlterField(
            model_name='storecertificate',
            name='otop_regis',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/certificates'),
        ),
    ]