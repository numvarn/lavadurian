from django.db import models
from django.contrib.auth.models import User

from Cart.choice import PROVINCE_CHOICE
from Store.models import Product, Store, BookBank, PathAndRename

import pytz
import datetime
import timeago
from datetime import datetime

ORDER_STATUS_CHOICES = (
    (1, 'รอรับออร์เดอร์'),
    (2, 'รับออร์เดอร์'),
    (3, 'รอการชำระเงิน'),
    (4, 'แจ้งชำระเงินแล้ว'),
    (5, 'ชำระเงินแล้ว'),
    (6, 'จัดส่งสินค้าแล้ว'),
    (7, 'ดำเนินการเสร็จสิ้น'),
    (8, 'ยกเลิก'),
)

TRACKER_STATUS_CHOICES = (
    (101, 'เตรียมการฝากส่ง'),
    (102, 'รับฝากผ่านตัวแทน'),
    (103, 'รับฝาก'),
    (201, 'อยู่ระหว่างการขนส่ง'),
    (202, 'ดำเนินพิธีการศุลกากร'),
    (203, 'ส่งคืนต้นทาง'),
    (301, 'อยู่ระหว่างการนำจ่าย'),
    (302, 'นำจ่าย ณ จุดรับสิ่งของ'),
    (401, 'นำจ่ายไม่สำเร็จ'),
    (501, 'นำจ่ายสำเร็จ'),
    (204, 'ถึงที่ทำการแลกปลี่ยนระหว่างประเทศขาออก'),
    (205, 'ถึงที่ทำการแลกปลี่ยนระหว่างประเทศขาเข้า'),
    (206, 'ถึงที่ทำการไปรษณีย์'),
    (207, 'เตรียมการขนส่ง'),
)

'''
# * This Function is used for rename files && images
# * before upload by FileField or ImageField
'''

slip_img_path = PathAndRename("uploads/slip_imgs")

# * ----------------------------------------------------


def thai_time(utc_date):
    if utc_date != '':
        tz = pytz.timezone('Asia/Bangkok')

        local_dt = utc_date.replace(tzinfo=pytz.utc).astimezone(tz)
        now1 = tz.normalize(local_dt)

        month_name = 'x มกราคม กุมภาพันธ์ มีนาคม เมษายน พฤษภาคม มิถุนายน กรกฎาคม สิงหาคม กันยายน ตุลาคม พฤศจิกายน ธันวาคม'.split()[
            now1.month]
        thai_year = now1.year + 543
        time_str = now1.strftime('%H:%M')

        # 30 ตุลาคม 2560 20:45:30
        return "%d %s %d %s" % (now1.day, month_name, thai_year, time_str)
    else:
        return '-'

# Mapping Chice : int to string


def getModelChoice(intValue, choices):
    choice_result = ''
    for choice in choices:
        if choice[0] == intValue:
            choice_result = choice[1]
            break
    return choice_result


class Cart(models.Model):
    session_key = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class ReceiveAddress(models.Model):
    name = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    address = models.TextField()
    province = models.IntegerField(choices=PROVINCE_CHOICE)
    postcode = models.CharField(max_length=10)
    phone = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.receiver+", "+self.address+" จังหวัด "+getModelChoice(self.province, PROVINCE_CHOICE)+", "+self.postcode+", โทร: "+self.phone


class AddressBook(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    receive_address = models.ManyToManyField(ReceiveAddress)


class Order(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    receive_address = models.ForeignKey(
        ReceiveAddress, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    status = models.IntegerField(choices=ORDER_STATUS_CHOICES, default=1)
    customer_request = models.TextField(blank=True, null=True)
    weight = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    box_1 = models.IntegerField(default=0)
    box_2 = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    @property
    def order_date(self):
        return thai_time(self.date_created)

    @property
    def time_ago(self):
        tz = pytz.timezone('Asia/Bangkok')
        now = datetime.now(tz)
        date = self.date_created
        return timeago.format(date, now, 'th')

    """ @property
    def cost(self):
        total_item_price = 0
        itemAll = OrderItem.objects.filter(order=self)
        for subItem in itemAll:
            total_item_price += subItem.price
        return int(total_item_price)

    @property
    def total_price(self):
        total_item_price = 0
        total_price = 0

        itemAll = OrderItem.objects.filter(order=self)
        for subItem in itemAll:
            total_item_price += subItem.price

        total_price = total_item_price + self.box_1 + self.box_2 + self.shipping

        return int(total_price) """

    def __str__(self):
        return "ID"+str(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    price_kg = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)
    weight = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)
    date_created = models.DateTimeField(auto_now_add=True)


class OrderBox(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    boxsize_1 = models.IntegerField(default=1)
    boxsize_2 = models.IntegerField(default=1)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class OrderTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    tracker = models.CharField(max_length=255)
    status = models.IntegerField(choices=TRACKER_STATUS_CHOICES, default=101)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    @ property
    def store_name(self):
        return self.store.name

    @ property
    def send_date(self):
        return thai_time(self.date_created)

    @ property
    def update_date(self):
        return thai_time(self.date_updated)

    @ property
    def transfer_time(self):
        date_update = self.date_updated
        date_start = self.date_created
        return timeago.format(date_start, date_update, 'th')


class OrderMessage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)


class TransferNotification(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    bookbank = models.ForeignKey(BookBank, on_delete=models.CASCADE)
    transfer_date = models.DateTimeField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=slip_img_path)
    date_created = models.DateTimeField(auto_now_add=True)
