# Generated by Django 3.0.2 on 2020-06-05 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0008_auto_20200506_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='district',
            field=models.IntegerField(blank=True, choices=[(1, 'กันทรลักษณ์'), (2, 'ขุนหาญ'), (3, 'ศรีรัตนะ')], null=True),
        ),
        migrations.AlterField(
            model_name='bookbank',
            name='bank',
            field=models.CharField(choices=[('002', 'ธนาคารกรุงเทพ'), ('004', 'ธนาคารกสิกรไทย'), ('006', 'ธนาคารกรุงไทย'), ('011', 'ธนาคารทหารไทย'), ('014', 'ธนาคารไทยพาณิชย์'), ('025', 'ธนาคารกรุงศรีอยุธยา'), ('030', 'ธนาคารออมสิน'), ('034', 'ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร')], max_length=5),
        ),
        migrations.AlterField(
            model_name='product',
            name='gene',
            field=models.IntegerField(choices=[(1, 'ทุเรียนภูเขาไฟ (หมอนทอง)'), (2, 'ก้านยาว'), (3, 'หมอนทอง'), (4, 'ชะนี'), (5, 'กระดุม'), (6, 'หลงลับแล'), (7, 'พวงมณี')], default=1),
        ),
        migrations.AlterField(
            model_name='product',
            name='grade',
            field=models.IntegerField(choices=[(1, 'เกรดคุณภาพ'), (2, 'เกรดพรีเมี่ยม')], default=1),
        ),
    ]