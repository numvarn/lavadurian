# Generated by Django 3.1.7 on 2021-05-03 09:37

import Store.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0013_auto_20210425_2147'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialQRCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social', models.IntegerField(choices=[(1, 'FACEBOOK'), (2, 'LINE')])),
                ('qr_code', models.ImageField(upload_to=Store.models.PathAndRename('upload/qrcode_img'))),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Store.store')),
            ],
        ),
    ]
