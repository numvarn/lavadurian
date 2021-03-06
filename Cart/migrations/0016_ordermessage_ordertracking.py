# Generated by Django 3.0.2 on 2020-05-18 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Cart', '0015_auto_20200517_1438'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderTracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tracker', models.CharField(max_length=255)),
                ('status', models.IntegerField(choices=[(101, 'เตรียมการฝากส่ง'), (102, 'รับฝากผ่านตัวแทน'), (103, 'รับฝาก'), (201, 'อยู่ระหว่างการขนส่ง'), (202, 'ดำเนินพิธีการศุลกากร'), (203, 'ส่งคืนต้นทาง'), (301, 'อยู่ระหว่างการนำจ่าย'), (302, 'นำจ่าย ณ จุดรับสิ่งของ'), (401, 'นำจ่ายไม่สำเร็จ'), (501, 'นำจ่ายสำเร็จ'), (204, 'ถึงที่ทำการแลกปลี่ยนระหว่างประเทศขาออก'), (205, 'ถึงที่ทำการแลกปลี่ยนระหว่างประเทศขาเข้า'), (206, 'ถึงที่ทำการไปรษณีย์'), (207, 'เตรียมการขนส่ง')], default=101)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cart.Order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cart.Order')),
            ],
        ),
    ]
