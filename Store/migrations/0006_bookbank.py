# Generated by Django 3.0.2 on 2020-05-02 08:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0005_auto_20200426_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookBank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank', models.CharField(choices=[('002', 'ธนาคารกรุงเทพ'), ('004', 'ธนาคารกสิกรไทย'), ('006', 'ธนาคารกรุงไทย'), ('011', 'ธนาคารทหารไทย'), ('014', 'ธนาคารไทยพาณิชย์'), ('025', 'ธนาคารกรุงศรีอยุธยา'), ('030', 'ธนาคารออมสิน')], max_length=5)),
                ('bank_branch', models.CharField(max_length=255)),
                ('account_type', models.IntegerField(choices=[(1, 'กระแสรายวัน'), (2, 'ออมทรัพย์'), (3, 'เงินฝากประจำ')])),
                ('account_name', models.CharField(max_length=255)),
                ('account_number', models.CharField(max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Store.Store')),
            ],
        ),
    ]
