import os
from datetime import timedelta

from celery import Celery

# Set the default Django settings module for the 'celery' program.
from celery.schedules import crontab
from datetime import timedelta
from main import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main', include=[])


""" app.conf.beat_schedule = {
    'realtime_options':{
        'task':'options_realtime_process',
        'schedule':1,
        'relative':True
    },
    'realtime_instrument_synch':{
        'task':'update_realtime_instruments',
        'schedule':1,
        'relative':True
    },
    #'realtime_entryexit':{
    #    'task':'entryexit_realtime_process',
    #    'schedule':1,
    #    'relative':True
    #},
    #'realtime_entryexit_backup':{
    #    'task':'entryexit_backup',
    #    'schedule':crontab(minute='*/5', hour='3-10', day_of_week='1-5'),
    #    'relative':True
    #},
    # 'make_minutes_from_ticks':{
    #     'task':'minute_maker',
    #     'schedule':1,
    #     'relative':True
    # },
    'historic_candle_synch':{
        'task':'candles_sync_historic',
        'schedule':crontab(minute='*/1', hour='3-10', day_of_week='1-5'),
        'relative':True
    },
    'check_for_ticker_restart':{
        'task':'ticker_checker',
        'schedule':crontab(minute='*/4', hour='3-10', day_of_week='1-5'),
        'relative':True
    },
    'backup_option_strategy_objects':{
        'task':'options_backup',
        'schedule':crontab(minute='*/2', hour='3-10', day_of_week='1-5'),
        'relative':True
    },
    'get_options_from_kite':{
        'task':'get_all_option_instruments',
        'schedule':crontab(hour=10, minute=5, day_of_week='1-5'),
        'relative':True
    },
    'data_reset':{
        'task':'daily_realtime_data_reset',
        'schedule':crontab(minute=35, hour=3, day_of_week='1-5'),
        'relative':True
    },
    'daily_get_futures':{
        'task':'get_futures',
        'schedule':crontab(minute=38, hour=3, day_of_week='1-5'),
        'relative':True
    },
    # 'daily_check_futures_expiry':{
    #     'task':'check_futures_expiry',
    #     'schedule':crontab(minute=37, hour=3, day_of_week='1-5'),
    #     'relative':True
    # }
    # 'double_test_task':{
    #     'task':'test_task',
    #     'schedule':5,
    #     'relative':True
    # }


} """

CELERY_TIMEZONE = 'Asia/Kolkata'
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')
#CELERY_BROKER_URL = 'amqp://guest:guest@localhost:15672/'
# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda:settings.INSTALLED_APPS)
BROKER_CONNECTION_RETRY = True
BROKER_CONNECTION_MAX_RETRIES = 0
BROKER_CONNECTION_TIMEOUT = 10120
