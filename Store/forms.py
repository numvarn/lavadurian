from django.forms import ModelForm
from Store.models import BookBank, Product, ProductImages, Store, StoreCertificate, Review
from django import forms

SCORE_CHOICES=[
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5)
]

class CreateStoreForm(ModelForm):
    class Meta:
        model = Store
        fields = ['owner', 'name', 'district', 'slogan', 'about', 'phone1', 'phone2', 'status']
        labels = {
            'name': 'ชื่อร้านค้า',
            'district': 'เขตอำเภอ',
            'slogan': 'สโลแกนร้านค้า',
            'about': 'เกี่ยวกับร้านค้า',
            'phone1': 'เบอร์โทรติดต่อหลัก',
            'phone2': 'เบอร์โทรติดต่อสำรอง (ถ้ามี)',
            'status': 'สถานะร้านค้า'
        }

class AddProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        labels = {
            'grade': 'เกรดทุเรียน',
            'gene': 'สายพันธุ์',
            'values': 'จำนวนที่มีขาย (ลูก)',
            'price': 'ราคาต่อกิโลกรัม',
            'weight': 'น้ำหนักเฉลี่ยต่อลูก',
            'desc': 'รายละเอียดเพิ่มเติม',
            'status': 'สถานะการขาย',
        }

class ProductImageForm(ModelForm):
    image = forms.ImageField(label='Image') 
    class Meta:
        model = ProductImages
        fields = ('image',)
        labels = {
            'image': 'ภาพสินค้า',
        }

class StoreCertificateForm(ModelForm):
    class Meta:
        model = StoreCertificate
        fields = '__all__'
        labels = {
            'commercial_regis': 'ทะเบียนพาณิช',
            'food_storage_license': 'ใบอนุญาตสะสมอาหาร',
            'gmp_regis': 'ใบประกาศ GMP',
            'otop_regis': 'ใบประกาศ OTOP',
        }

class BankForm(ModelForm):
    class Meta:
        model = BookBank
        fields = '__all__'
        labels = {
            'store': 'ร้านค้า',
            'bank': 'ธนาคาร',
            'bank_branch': 'สาขา',
            'account_type': 'ประเภท',
            'account_name': 'ชื่อบัญชี',
            'account_number': 'เลขบัญชี',
        }

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ('store', 'reviewer', 'order', 'product', 'score', 'comment')
        
        widgets = {
            'comment': forms.Textarea(attrs={'rows':3}),
        }
        labels = {
            'store': 'ร้านค้า',
            'product': 'สิ้นค้า',
            'order': 'หมายเลขคำสั่งซื้อ',
            'reviewer': 'ผู้รีวิว',
            'comment': 'ข้อความ',
            'score': 'ให้คะแนนสินค้า',
        }
