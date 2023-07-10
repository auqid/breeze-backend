import os
from celery.utils.log import get_task_logger
from celery import shared_task
from core.models import Stock,Instrument,NFO_Stock
from datetime import datetime
logger = get_task_logger(__name__)


@shared_task(name="load stocks") 
def load_data():
    instruments = Instrument.objects.all()
    for ins in instruments:
        for line in ins.file:
            line = line.decode().split(',')
            data = [item.replace('"','')for item in line]
            #print(data)
            try:
                if ins.is_option:# Futures and options
                    if NFO_Stock.objects.filter(token =data[0]).exists():
                        pass
                    else:
                        if data[0] == 'Token':
                            pass
                        else:
                            sub_load.delay(ins.code,data,False)
                else:# normal Stock
                    if Stock.objects.filter(token =data[0]).exists():
                        pass
                    else:
                        if data[0] == 'Token':
                            pass
                        else:
                            sub_load.delay(ins.code,data,True)
            except Exception as e:
                print(e)

@shared_task(name="sub load task")
def sub_load(stock_token_code,data,is_stock):
    #print('sub loading')
    if is_stock:
        stock = Stock(
            stock_token = stock_token_code+'.1!'+data[0],
            token=data[0],
            short_name=data[1],
            series=data[2],
            company_name=data[3],
            exchange_code=data[-1] if data[-1][-2:] != "\r\n" else data[-1][:-2]
        )
        stock.save()
    else:
        stock = NFO_Stock(
            stock_token = stock_token_code+'.1!'+data[0],
            token=data[0],
            instrument=data[1],
            short_name=data[2],
            series=data[3],
            expiry=datetime.strptime(data[4], '%d-%b-%Y').date(),
            strike_price = float(data[5]),
            option_type = data[6],
            exchange_code=data[-1] if data[-1][-2:] != "\r\n" else data[-1][:-2]
        )
        stock.save()
    ... 