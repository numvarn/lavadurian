# Generated by Django 3.2.12 on 2023-05-29 00:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0017_storelocation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='district',
            field=models.IntegerField(blank=True, choices=[(1, 'กันทรลักษ์'), (2, 'ขุนหาญ'), (3, 'ศรีรัตนะ')], null=True),
        ),
    ]