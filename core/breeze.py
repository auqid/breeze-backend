from breeze_connect import BreezeConnect
from core.models import BreezeAccount
from main.settings import BREEZE_SESSION

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



""" # Initialize SDK
breeze = BreezeConnect(api_key="9D0l477St3656309C2970878F$707K5Y")

# Obtain your session key from https://api.icicidirect.com/apiuser/login?api_key=9D0l477St3656309C2970878F$707K5Y
# Incase your api-key has special characters(like +,=,!) then encode the api key before using in the url as shown below.
import urllib
print("https://api.icicidirect.com/apiuser/login?api_key="+urllib.parse.quote_plus("9D0l477St3656309C2970878F$707K5Y"))


session_token = "15057684"
# Generate Session
breeze.generate_session(api_secret="Z9R5=441o98gmB74I635650547m25N77",
                        session_token=session_token)


breeze.ws_connect()

def on_ticks(ticks):
    #print("Ticks: {}".format(ticks))
    print("--------------------------------")
    print(ticks)
    print("--------------------------------")

breeze.on_ticks = on_ticks



breeze.subscribe_feeds(stock_token="4.1!NIFTY 50")
breeze.subscribe_feeds(stock_token="4.1!42697")

instruments = breeze.get_names(exchange_code="NFO", stock_code="NIFTY 50")
print(instruments) """
