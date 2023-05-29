from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.deconstruct import deconstructible
from uuid import uuid4
from django.dispatch import receiver
from google.cloud import storage
import pytz
import os

'''
# * This Function is used for rename files && images 
# * before upload by FileField or ImageField
'''


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)


product_img_path = PathAndRename("uploads/product_imgs")
qrcode_path = PathAndRename("uploads/qrcode_img")

# * ----------------------------------------------------

# Create your models here.
SCORE_CHOICES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)

STATUS_CHOICES = (
    (0, 'รอการอนุมัติ'),
    (1, 'เปิดร้าน'),
    (2, 'ปิดร้าน'),
    (3, 'ไม่พร้อมขาย'),
)

GRADE_CHOICES = (
    (1, 'เกรดคุณภาพ'),
    (2, 'เกรดพรีเมี่ยม'),
)

GENE_CHOICES = (
    (1, 'ทุเรียนภูเขาไฟ (หมอนทอง)'),
    (2, 'ก้านยาว'),
    (3, 'หมอนทอง'),
    (4, 'ชะนี'),
    (5, 'กระดุม'),
    (6, 'หลงลับแล'),
    (7, 'พวงมณี'),
)

DISTRICT_CHOICES = (
    # (1, 'กันทรลักษณ์'),
    (1, 'กันทรลักษ์'),
    (2, 'ขุนหาญ'),
    (3, 'ศรีรัตนะ'),
)

PRODUCT_STATUS_CHOICES = (
    (1, 'พร้อมขาย'),
    (2, 'สั่งจองล่วงหน้า'),
    (3, 'ยุติการขาย'),
)

BANK = (
    ("002", "ธนาคารกรุงเทพ"),
    ("004", "ธนาคารกสิกรไทย"),
    ("006", "ธนาคารกรุงไทย"),
    ("011", "ธนาคารทหารไทย"),
    ("014", "ธนาคารไทยพาณิชย์"),
    ("025", "ธนาคารกรุงศรีอยุธยา"),
    ("030", "ธนาคารออมสิน"),
    ("034", "ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร"),
)

ACCOUNT_TYPE = (
    (1, "กระแสรายวัน"),
    (2, "ออมทรัพย์"),
    (3, "เงินฝากประจำ"),
)

SOCIAL_TYPE = (
    (1, "FACEBOOK"),
    (2, "LINE"),
)

PRICE_FILTER = (
    ('80_120', '80 - 120 บาท/กก.'),
    ('120_160', '120 - 160 บาท/กก.'),
    ('160_200', '160 - 200 บาท/กก.'),
    ('200_240', '200 - 240 บาท/กก.'),
    ('240_1000', '240 บาทขึ้นไป'),
)

WEIGHT_FILTER = (
    ('0.5_0.8', 'น้ำหนัก 0.5 - 0.8 กก.'),
    ('0.9_1.2', 'น้ำหนัก 0.9 - 1.2 กก.'),
    ('1.3_1.5', 'น้ำหนัก 1.3 - 1.5 กก.'),
    ('1.6_2.0', 'น้ำหนัก 1.6 - 2.0 กก.'),
    ('2.1_2.5', 'น้ำหนัก 2.1 - 2.5 กก.'),
    ('2.6_5', 'น้ำหนัก 2.6 ขึ้นไป'),
)


class Store(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slogan = models.CharField(max_length=255)
    about = models.TextField()
    phone1 = models.CharField(max_length=255)
    phone2 = models.CharField(max_length=255, blank=True, null=True)
    district = models.IntegerField(
        choices=DISTRICT_CHOICES, blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def date_created_thai(self):
        return self.thai_time(self.date_created)

    def thai_time(self, utc_date):
        if utc_date != '':
            tz = pytz.timezone('Asia/Bangkok')

            local_dt = utc_date.replace(tzinfo=pytz.utc).astimezone(tz)
            now1 = tz.normalize(local_dt)

            month_name = 'x มกราคม กุมภาพันธ์ มีนาคม เมษายน พฤษภาคม มิถุนายน กรกฎาคม สิงหาคม กันยายน ตุลาคม พฤศจิกายน ธันวาคม'.split()[
                now1.month]
            thai_year = now1.year + 543
            time_str = now1.strftime('%H:%M')
            # time_str = now1.strftime('%H:%M:%S')

            # 30 ตุลาคม 2560 20:45:30
            return "%d %s %d %s" % (now1.day, month_name, thai_year, time_str)
        else:
            return '-'


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    grade = models.IntegerField(choices=GRADE_CHOICES, default=1)
    gene = models.IntegerField(choices=GENE_CHOICES, default=1)
    values = models.IntegerField()
    price = models.DecimalField(max_digits=9, decimal_places=2)
    weight = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)
    desc = models.TextField(null=True, blank=True)
    status = models.IntegerField(choices=PRODUCT_STATUS_CHOICES, default=1)
    date_created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        for choice in GENE_CHOICES:
            if choice[0] == self.gene:
                return choice[1]


class Review(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.IntegerField()
    comment = models.TextField()
    score = models.IntegerField(choices=SCORE_CHOICES)
    date_review = models.DateTimeField(auto_now_add=True)


class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_img_path)


class StoreCertificate(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    commercial_regis = models.ImageField(
        upload_to='uploads/certificates', blank=True, null=True)
    food_storage_license = models.ImageField(
        upload_to='uploads/certificates', blank=True, null=True)
    gmp_regis = models.ImageField(
        upload_to='uploads/certificates', blank=True, null=True)
    otop_regis = models.ImageField(
        upload_to='uploads/certificates', blank=True, null=True)


class BookBank(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    bank = models.CharField(max_length=5, choices=BANK)
    bank_branch = models.CharField(max_length=255)
    account_type = models.IntegerField(choices=ACCOUNT_TYPE)
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        bank_choice = ''
        for choice in BANK:
            if choice[0] == self.bank:
                bank_choice = choice[1]
                break
        return bank_choice+" : "+self.bank_branch+" : "+self.account_name


class SocialQRCode(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    social = models.IntegerField(choices=SOCIAL_TYPE)
    qr_code = models.ImageField(upload_to=qrcode_path)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "QR Code of {} : {}".format(self.store, dict(SOCIAL_TYPE)[self.social])


class StoreLocation(models.Model):
    """Model definition for StoreLocation."""

    # TODO: Define fields here
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    date_created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for StoreLocation."""

        verbose_name = 'StoreLocation'
        verbose_name_plural = 'StoreLocations'

    def __str__(self):
        """Unicode representation of StoreLocation."""
        return self.store.name


'''
# * This Function is used for delete files && images 
# * before delete FileField or ImageField in model
'''


@receiver(models.signals.post_delete, sender=ProductImages)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file in bucket form Google Cloud Storage
    when corresponding `MediaFile` object is deleted.
    """
    storage_client = storage.Client(credentials=settings.GS_CREDENTIALS)
    bucket = storage_client.get_bucket(settings.GS_BUCKET_NAME)

    # check file is exist
    stats = storage.Blob(
        bucket=bucket, name=instance.image.name).exists(storage_client)

    if stats and instance.image:
        bucket.delete_blob(instance.image.name)
        return '{} deleted from bucket.'.format(instance.image.name)


@receiver(models.signals.post_delete, sender=SocialQRCode)
def auto_delete_qrcode_on_delete(sender, instance, **kwargs):
    storage_client = storage.Client(credentials=settings.GS_CREDENTIALS)
    bucket = storage_client.get_bucket(settings.GS_BUCKET_NAME)

    # check file is exist
    stats = storage.Blob(
        bucket=bucket, name=instance.qr_code.name).exists(storage_client)

    if stats and instance.qr_code:
        bucket.delete_blob(instance.qr_code.name)
        return '{} deleted from bucket.'.format(instance.qr_code.name)
