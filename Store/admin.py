from django.contrib import admin
from django.contrib.auth.models import User
from Store.models import Product, ProductImages, Review, SocialQRCode, Store, StoreCertificate, BookBank, StoreLocation, RecommendedProduct
from Store.forms import CreateStoreForm
from django.contrib.auth.decorators import user_passes_test
from django.utils.html import format_html
from Members.models import Trader

'''
# * Create Django Admin List Actions
'''

"""
* Action for product
"""


def make_product_ready_for_selling(modeladmin, request, queryset):
    queryset.update(status='1')


def make_product_preorder_for_selling(modeladmin, request, queryset):
    queryset.update(status='2')


def make_product_stop_selling(modeladmin, request, queryset):
    queryset.update(status='3')


make_product_ready_for_selling.short_description = 'ปรับสถานะสินค้าเป็น "พร้อมขาย"'
make_product_preorder_for_selling.short_description = 'ปรับสถานะสินค้าเป็น "สั่งจองล่วงหน้า"'
make_product_stop_selling.short_description = 'ปรับสถานะสินค้าเป็น "ยุติการขาย"'

""" 
* Action for store
"""


def make_store_awit_approval(modeladmin, request, queryset):
    queryset.update(status='0')


def make_store_opened(modeladmin, request, queryset):
    queryset.update(status='1')


def make_store_closed(modeladmin, request, queryset):
    queryset.update(status='2')


def make_store_not_ready_for_sale(modeladmin, request, queryset):
    queryset.update(status='3')


make_store_awit_approval.short_description = 'รอการอนุมัติ'
make_store_opened.short_description = 'เปิดร้าน'
make_store_closed.short_description = 'ปิดร้าน'
make_store_not_ready_for_sale.short_description = 'ไม่พร้อมขาย'

# --------------------------------------------


class ProductAdmin(admin.ModelAdmin):
    list_display = ('grade', 'gene', 'values', 'price',
                    'weight', 'status', 'store', 'date_update')
    search_fields = ('store__name',)
    list_filter = ('status',)
    actions = [make_product_ready_for_selling,
               make_product_preorder_for_selling, make_product_stop_selling, ]


class StoreAdmin(admin.ModelAdmin):
    form = CreateStoreForm

    list_display = ('name', 'owner_url_field', 'district',
                    'phone1', 'phone2', 'status', 'date_created_thai')
    search_fields = ('name', 'owner__first_name', 'owner__last_name',)
    list_filter = ('status', 'district')

    actions = [make_store_awit_approval, make_store_opened,
               make_store_closed, make_store_not_ready_for_sale, ]

    # Action save model
    def save_model(self, request, obj, form, change):
        if self.in_group(request.user, "trader") and not self.in_group(request.user, "manager") and not request.is_superuser:
            obj.owner = request.user

        super().save_model(request, obj, form, change)

    # check group
    def in_group(self, u, group_names):
        return u.is_active and (u.is_superuser or bool(u.groups.filter(name__in=group_names)))

    # link to owner
    def owner_url_field(self, obj):
        # get trader
        query = Trader.objects.filter(account=obj.owner)
        if len(query) > 0:
            trader = query[0]
            link = '/admin/Members/trader/'+str(trader.id)+'/change/'
            return format_html('<a href="%s" target="_blank">%s</a>' % (link, obj.owner))
        else:
            return "no owner"

    owner_url_field.short_description = 'Store Owner'


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'store',
                    'reviewer', 'comment', 'score')
    list_filter = ('score', )
    search_fields = ('store__name', )


class SocialQRCodeAdmin(admin.ModelAdmin):
    list_display = ('store', 'social', 'date_created')


@admin.register(RecommendedProduct)
class RecommendedProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_desc', 'link')


admin.site.register(Product, ProductAdmin)
admin.site.register(StoreCertificate)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(ProductImages)
admin.site.register(BookBank)
admin.site.register(SocialQRCode, SocialQRCodeAdmin)
admin.site.register(StoreLocation)
