from django.contrib import admin
from Members.models import Trader, registerGI


class TraderAdmin(admin.ModelAdmin):
    list_display = ('account', 'trader_type', 'phone',
                    'date_regis_thai', 'store_count')
    list_filter = ('trader_type', )
    search_fields = ('account__first_name', 'account__last_name')


# Register your models here.
admin.site.register(Trader, TraderAdmin)


@admin.register(registerGI)
class registerGIAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'subdistrict',
                    'district', 'province', 'phone')

    search_fields = ('first_name', 'last_name')
