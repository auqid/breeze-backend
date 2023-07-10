from django.contrib import admin
from core.models import Instrument,Stock,NFO_Stock,BreezeAccount
# Register your models here.
class StockAdmin(admin.ModelAdmin):
    search_fields = ['short_name', 'exchange_code']

class NFO_StockAdmin(admin.ModelAdmin):
    search_fields = ['short_name', 'strike_price','option_type','exchange_code','series']


admin.site.register(Instrument)
admin.site.register(Stock,StockAdmin)
admin.site.register(NFO_Stock,NFO_StockAdmin)
admin.site.register(BreezeAccount)