import os
import zipfile
import shutil
import numpy as np
import urllib.request
from main.settings import MEDIA_ROOT
from celery.utils.log import get_task_logger
from celery import shared_task
from core.models import Exchanges,Instrument
from datetime import datetime
logger = get_task_logger(__name__)


@shared_task(name='get_master_files')
def get_master_data():
    url = 'https://directlink.icicidirect.com/NewSecurityMaster/SecurityMaster.zip'
    zip_path = MEDIA_ROOT+'SecurityMaster.zip'
    extracted_path = MEDIA_ROOT+'extracted/'
    try:
        shutil.rmtree(extracted_path)
    except:
        pass
    urllib.request.urlretrieve(url, zip_path)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extracted_path)

    for extracted_file in zf.namelist():
        #print("File:", extracted_file[:3])
        ins = Exchanges.objects.filter(title=extracted_file[:3])
        if ins.exists():
            ins.update(file=extracted_file)
        else:#first time
            title = extracted_file[:3]
            if title == 'BSE':
                new_ins = Exchanges(title=title,file='extracted/'+extracted_file,code='1',exchange='BSE')
                new_ins.save()
            if title == 'CDN':
                pass
            if title == 'FON':
                new_ins = Exchanges(title=title,file='extracted/'+extracted_file,code='4',exchange='NFO',is_option=True)
                new_ins.save()
            if title == 'NSE':
                new_ins = Exchanges(title=title,file='extracted/'+extracted_file,code='4',exchange='NSE')
                new_ins.save()

    
    os.remove(zip_path)
    #shutil.rmtree(extracted_path)

@shared_task(name="load stocks") 
def load_data(id):
    ins = Exchanges.objects.get(id=id)
    ins_list = []
    
    for line in ins.file:
        line = line.decode().split(',')
        data = [item.replace('"','')for item in line]
        if ins.is_option:# Futures and options
            if Instrument.objects.filter(token =data[0]).exists():
                pass
            else:
                if data[0] == 'Token':
                    pass
                else:
                    stock = Instrument(
                        exchange = ins,
                        stock_token = ins.code+'.1!'+data[0],
                        token=data[0],
                        instrument=data[1],
                        short_name=data[2],
                        series=data[3],
                        company_name=data[3],
                        expiry=datetime.strptime(data[4], '%d-%b-%Y').date(),
                        strike_price = float(data[5]),
                        option_type = data[6],
                        exchange_code=data[-1] if data[-1][-2:] != "\r\n" else data[-1][:-2]
                        )
                    ins_list.append(stock)
        else:# normal Stock
            if Instrument.objects.filter(token =data[0]).exists():
                pass
            else:
                if data[0] == 'Token':
                    pass
                else:
                    stock = Instrument(
                        exchange = ins,
                        stock_token = ins.code+'.1!'+data[0],
                        token=data[0],
                        short_name=data[1],
                        series=data[2],
                        company_name=data[3],
                        exchange_code=data[-1] if data[-1][-2:] != "\r\n" else data[-1][:-2]
                        )
                    ins_list.append(stock)
    our_array = np.array(ins_list)
    chunk_size = 800
    chunked_arrays = np.array_split(our_array, len(ins_list) // chunk_size + 1)
    chunked_list = [list(array) for array in chunked_arrays]
    for ch in chunked_list:
        Instrument.objects.bulk_create(ch)


