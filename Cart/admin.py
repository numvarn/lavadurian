from django.contrib import admin
from Cart.models import AddressBook, Cart, CartItem, Order, OrderItem, OrderMessage, OrderTracking, ReceiveAddress, TransferNotification, OrderBox
# Register your models here.


class CartAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'date_created', )


class ItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', )


class OrderAdmin(admin.ModelAdmin):
    list_display = ('owner', 'store', 'weight', 'shipping',
                    'box_1', 'box_2', 'status', 'order_date', 'time_ago')
    search_fields = ('store__name', 'owner__first_name', 'owner__last_name')
    list_filter = ('status', )


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_kg',
                    'weight', 'price', 'date_created')


class TransferNotificationAdmin(admin.ModelAdmin):
    list_display = ('order', 'transfer_date', 'note', 'date_created')


class OrderMessageAdmin(admin.ModelAdmin):
    list_display = ('order', 'message', 'date_created')


class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ('tracker', 'order', 'store_name', 'status',
                    'update_date', 'send_date', 'transfer_time')
    search_fields = ('order__id', 'store__name', 'tracker')
    list_filter = ('status', 'order__store__name')


class OrderBoxAdmin(admin.ModelAdmin):
    list_display = ('order', 'boxsize_1', 'boxsize_2', 'date_updated')


class ReceiveAddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'receiver', 'address',
                    'province', 'postcode', 'phone')


class AddressBookAdmin(admin.ModelAdmin):
    list_display = ('owner', )


admin.site.register(OrderTracking, OrderTrackingAdmin)
admin.site.register(OrderMessage, OrderMessageAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, ItemAdmin)
admin.site.register(ReceiveAddress, ReceiveAddressAdmin)
admin.site.register(AddressBook, AddressBookAdmin)
admin.site.register(TransferNotification, TransferNotificationAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(OrderBox, OrderBoxAdmin)
