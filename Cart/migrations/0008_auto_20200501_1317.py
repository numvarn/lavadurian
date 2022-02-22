# Generated by Django 3.0.2 on 2020-05-01 06:17

import cloudinary.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Cart', '0007_auto_20200430_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'รอรับออร์เดอร์'), (2, 'รับออร์เดอร์'), (3, 'รอการชำระเงิน'), (4, 'แจ้งชำระเงินแล้ว'), (5, 'ชำระเงินแล้ว'), (6, 'จัดส่งสินค้าแล้ว'), (7, 'ดำเนินการเสร็จสิ้น'), (8, 'ยกเลิก')], default=1),
        ),
        migrations.CreateModel(
            name='TransferNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_date', models.DateTimeField()),
                ('note', models.TextField()),
                ('image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='image')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cart.Order')),
            ],
        ),
    ]
