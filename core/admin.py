from django.contrib import admin
from core.models import Exchanges,Instrument,BreezeAccount
# Register your models here.

class InstrumentAdmin(admin.ModelAdmin):
    #search_fields = ['short_name', 'strike_price','option_type','exchange_code','series']
    search_fields = ['short_name']


admin.site.register(Exchanges)
admin.site.register(Instrument,InstrumentAdmin)
admin.site.register(BreezeAccount)