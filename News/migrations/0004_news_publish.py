# Generated by Django 3.0.2 on 2020-04-19 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('News', '0003_news_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='publish',
            field=models.IntegerField(choices=[(0, 'PUBLISH'), (1, 'NOT PUBLISH')], default=0),
        ),
    ]
