from django.forms import ModelForm
from django import forms
from Cart.models import Order, OrderItem, OrderMessage, OrderTracking, ReceiveAddress, TransferNotification
from Store.models import BookBank

class ReceiveAddressForm(ModelForm):
    class Meta:
        model = ReceiveAddress
        fields = ('name', 'receiver', 'phone', 'address', 'province', 'postcode')
        widgets = {
            'address': forms.Textarea(attrs={'rows':2}),
        }
        labels = {
            'name': 'ตั้งชื่อบัญชีที่อยู่ (สำหรับช่วยจำ)', 
            'receiver': 'ชื่อ-สกุล ผู้รับสินค้า',
            'address': 'ที่อยู่จัดส่ง', 
            'province': 'จังหวัด', 
            'postcode': 'รหัสไปรษณีย์',
            'phone': 'เบอร์โทรติดต่อ',
        }

class SetOrderStatus(ModelForm):
    class Meta:
        model = Order
        fields = ('status',)
        labels = {
            'status': 'สถานะการสั่งซื้อ',
        }

class TransferNotificationForm(ModelForm):
    class Meta:
        model = TransferNotification
        fields = ('order', 'transfer_date', 'bookbank', 'note', 'image')
        
        widgets = {
            'transfer_date': forms.DateTimeInput(attrs={'id':'datetimepicker'}),
            'note': forms.Textarea(attrs={'rows':2}),
        }
        
        labels = {
            'transfer_date': 'ระบุ วัน-เวลาที่โอนเงิน',
            'bookbank': 'บัญชีที่โอน',
            'note': 'ระบุหมายเหตุ (ถ้ามี)',
            'image': 'ภาพหลักฐานการแจ้งโอน'
        }

    def __init__(self, *args, **kwargs):
        super(TransferNotificationForm, self).__init__(*args, **kwargs)
        if kwargs.get('initial'):
            init = kwargs.pop('initial')
            store = init['store']
            self.fields['bookbank'].queryset = BookBank.objects.filter(store=store)

class OrderTrackingForm(ModelForm):
    class Meta:
        model = OrderTracking
        fields = ('order', 'store', 'tracker')
        widgets = {
            'order': forms.HiddenInput(),
            'store': forms.HiddenInput(),
        }
        labels = {
            'tracker': 'หมายเลขพัสดุ (สำหรับติดตามการขนส่ง)'
        }
        

class OrderMessageForm(ModelForm):
    class Meta:
        model = OrderMessage
        fields = ('order', 'message')
        widgets = {
            'order': forms.HiddenInput(),
            'message': forms.Textarea(attrs={'rows':2}),
        }
        labels = {
            'order': 'คำสั่งซื้อ',
            'message': 'ข้อความถึงลูกค้า',
        }

class OrderItemForm(ModelForm):
    class Meta:
        model = OrderItem
        fields = '__all__'
        widgets = {
            'order': forms.HiddenInput(),
            'product': forms.HiddenInput(),
            'price': forms.HiddenInput(),
            'price_kg': forms.HiddenInput(),
            'quantity': forms.HiddenInput(),
        }
        labels = {
            'order': 'คำสั่งซื้อ',
            'product': 'สินค้า',
            'quantity': 'จำนวน (ลูก)',
            'price': 'ราคารวม',
            'weight': 'น้ำหนัก (กก.)'
        }