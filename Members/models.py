from django.db import models
from django.contrib.auth.models import User
import pytz

from Store.models import Store

def get_users_name(self):
    return self.first_name+" "+self.last_name

User.add_to_class("__str__", get_users_name)

# Create your models here.
TRADER_CHOICES = (
    ('เจ้าของสวน','เจ้าของสวน'),
    ('ผู้ค้าคนกลาง', 'ผู้ค้าคนกลาง'),
)

class Trader(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE)
    citizen_id = models.CharField(max_length=13)
    trader_type = models.CharField(max_length=50, choices=TRADER_CHOICES)
    store_name = models.TextField()
    phone = models.CharField(max_length=255)
    date_regis = models.DateTimeField(auto_now=True)

    @property
    def date_regis_thai(self):
        return self.thai_time(self.date_regis)

    @property
    def store_count(self):
        return Store.objects.filter(owner=self.account).count()

    def thai_time(self, utc_date):
        if utc_date != '':
            tz = pytz.timezone('Asia/Bangkok')

            local_dt = utc_date.replace(tzinfo=pytz.utc).astimezone(tz)
            now1 = tz.normalize(local_dt)

            month_name = 'x มกราคม กุมภาพันธ์ มีนาคม เมษายน พฤษภาคม มิถุนายน กรกฎาคม สิงหาคม กันยายน ตุลาคม พฤศจิกายน ธันวาคม'.split()[now1.month]
            thai_year = now1.year + 543
            time_str = now1.strftime('%H:%M')
            # time_str = now1.strftime('%H:%M:%S')
            
            return "%d %s %d %s"%(now1.day, month_name, thai_year, time_str) # 30 ตุลาคม 2560 20:45:30
        else:
            return '-'
