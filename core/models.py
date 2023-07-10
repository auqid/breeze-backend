from django.db import models

# Create your models here.


class BreezeAccount(models.Model):
    name = models.CharField(default='ADMIN',max_length=255)
    api_key = models.CharField(default=' ',max_length=255)
    api_secret = models.CharField(default=' ',max_length=255)
    session_token = models.CharField(max_length=255,null=True,blank=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

class Exchanges(models.Model):
    title = models.CharField(default='NSE',max_length=255)
    file = models.FileField(blank=False)
    code = models.CharField(default='1',max_length=255)
    exchange = models.CharField(default='NSE',max_length=255)
    is_option = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.exchange)

class Instrument(models.Model):
    exchange = models.ForeignKey(Exchanges, on_delete=models.CASCADE)
    stock_token = models.CharField(blank=True,null=True,max_length=255)
    token = models.CharField(blank=True,null=True,max_length=255)
    instrument = models.CharField(null=True,blank=True,max_length=255)
    short_name = models.CharField(blank=True,null=True,max_length=255)
    series = models.CharField(blank=True,null=True,max_length=255)
    company_name = models.CharField(null=True,blank=True,max_length=255)
    expiry = models.DateField(blank=True,null=True)
    strike_price = models.FloatField(blank=True,null=True)
    option_type = models.CharField(blank=True,null=True,max_length=255)
    exchange_code = models.CharField(blank=True,null=True,max_length=255)

    def __str__(self):
        return "Token:"+str(self.token) +" Instrument:"+ str(self.instrument) +" Expiry:"+\
              str(self.expiry)+" Strike Price"+str(self.strike_price)