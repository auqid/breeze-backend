from breeze_connect import BreezeConnect
from core.models import BreezeAccount
from datetime import datetime
from core.helper import date_parser
class BreezeSession():
    def __init__(self):
        #if BREEZE_SESSION is None:
        self.acc = BreezeAccount.objects.all().last()
        self.breeze = BreezeConnect(api_key=self.acc.api_key)
        self.breeze.generate_session(api_secret=self.acc.api_secret,session_token=self.acc.session_token)
        #BREEZE_SESSION = self.breeze
        #else:
           #self.breeze = BREEZE_SESSION
        

    def websocket_start(self):
        self.breeze.ws_connect()
        def on_ticks(ticks):
            print("--------------------------------")
            print(ticks)
            print("--------------------------------")
        self.breeze.on_ticks = on_ticks
        self.breeze.subscribe_feeds(stock_token="4.1!NIFTY 50")
        self.breeze.subscribe_feeds(stock_token="4.1!42697")
    
    def get_data(self):
        data = self.breeze.get_historical_data_v2('1minute','2023-07-01T07:00:00.000Z','2023-07-10T07:00:00.000Z','NIFTY','NSE')
        data2 = self.breeze.get_historical_data_v2('1minute','2023-07-01T07:00:00.000Z','2023-07-10T07:00:00.000Z','NIFTY','NFO','futures','2023-07-27T07:00:00.000Z')
        print(data)



