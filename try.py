import websocket
import json
import hmac
import hashlib
try:
    import thread
except ImportError:
    import _thread as thread
import time
from statistics import median, stdev
import random
import requests
from datetime import datetime, timedelta

i = 0

frame = {'m':0,'i':0,'n':'','o':'{}'}

instruments  = {}

api_key = 'key'
user_id = str(00)
nonce = str(int(datetime.timestamp(datetime.now())))
api_secret = 'secret'
signature = hmac.new(bytes(api_secret,'utf-8'), msg = bytes('{nonce}{user_id}{api_key}'.format(nonce=nonce,user_id=user_id,api_key=api_key), 'utf-8'), digestmod = hashlib.sha256).hexdigest()

user = {
    "APIKey": api_key,
    "Signature": signature,
    "UserId": user_id,
    "Nonce": nonce
}

band_upper = []
band_medium = []
band_lower = []
last_traded_px = []

data_regression_base = []

len_regression_base = 1

def linear_regression(j):

    i = []

    ij = []

    ii = []

    jj = []

    for x in range(1,len(j)+1): i.append(x)

    for x in range(0,len(i)): ij.append(i[x]*j[x])

    for x in range(0,len(i)):
        ii.append(i[x]**2)
        jj.append(j[x]**2)

    b = (len(i)*sum(ij)-sum(i)*sum(j))/(len(i)*sum(ii)-(sum(i))**2)
    a = median(j)-b*median(i)

    r = []

    r.append(b)
    r.append(a)

    return r

def band(px,fn,sc,lm):

    global band_upper
    global band_medium
    global band_lower
    global last_traded_px

    if len(last_traded_px) > lm:
        last_traded_px.pop(0)

    if px not in last_traded_px:
        last_traded_px.append(px)

    if fn == 'u':

        if len(band_upper) > lm:
            band_upper.pop(0)

        if len(last_traded_px) > 2:
            
            new_band_upper =  median(last_traded_px)+sc*stdev(last_traded_px)

            if new_band_upper not in band_upper:
                band_upper.append(new_band_upper)

    elif fn == 'm':

        if len(band_medium) > lm:
            band_medium.pop(0)

        if len(last_traded_px) > 2:
            new_band_medium = median(last_traded_px)

            if new_band_medium not in band_medium:
                band_medium.append(new_band_medium)

    elif fn == 'l':

        if len(band_lower) > lm:
            band_lower.pop(0)

        if len(last_traded_px) > 2:
            new_band_lower =  median(last_traded_px)-sc*stdev(last_traded_px)

            if new_band_lower not in band_lower:
                band_lower.append(new_band_lower)

    else:
        pass

def on_open(ws):
    on_send(ws)

def on_message(ws, message):

    global instruments
    global i

    message = json.loads(message)

    if message['n'] == 'GetInstruments':

        message = json.loads(message['o'])
        for x in range(0,len(message)):

            if message[x]['Symbol'] == 'BTC/BRL':

                instruments[message[x]['InstrumentId']] = {
                    'Symbol': message[x]['Symbol']
                }

                send = {
                    'InstrumentId': 0
                }

                send['InstrumentId'] = message[x]['InstrumentId']

                frame['m'] = 0
                frame['i'] = i
                frame['n'] = 'SubscribeLevel1'
                frame['o'] = send

                on_send(ws)

    elif message['n'] == 'SubscribeLevel1':
        pass

    elif message['n'] == 'Level1UpdateEvent':
         
        message = json.loads(message['o'])
        instrument_id = message['InstrumentId']
        symbol = instruments[instrument_id]['Symbol']
        delay =  datetime.utcfromtimestamp(int(datetime.timestamp(datetime.now())) - message['TimeStamp']).microsecond

        px  = message['LastTradedPx']

        band(px,'u',2,100)
        band(px,'m',2,100)
        band(px,'l',2,100)

        instruments[instrument_id] = {
            'Symbol': symbol,
            'BestBid': float(message['BestBid']),
            'BestOffer': float(message['BestOffer']),
            'LastTradedPx': message['LastTradedPx'],
            'LastTradedQty': message['LastTradedQty'],
            'LastTradeTime': message['LastTradeTime'],
            'SessionOpen': message['SessionOpen'],
            'SessionHigh': message['SessionHigh'],
            'SessionLow': message['SessionLow'],
            'SessionClose': message['SessionClose'],
            'Volume': message['Volume'],
            'CurrentDayVolume': message['CurrentDayVolume'],
            'CurrentDayNumTrades': message['CurrentDayNumTrades'],
            'CurrentDayPxChange': message['CurrentDayPxChange'],
            'Rolling24HrVolume': message['Rolling24HrVolume'],
            'Rolling24NumTrades': message['Rolling24NumTrades'],
            'Rolling24HrPxChange': message['Rolling24HrPxChange'],
            'TimeStamp': message['TimeStamp'],
            'Delay': delay
        }

        i += 2
    
    elif message['n'] == 'AuthenticateUser':
        message = json.loads(message['o'])

        frame['m'] = 0
        frame['i'] = 0
        frame['n'] = 'LogOut'
        frame['o'] =  {}

        on_send(ws)

    else:
        pass

def on_send(ws):

    global frame

    frame['o'] = json.dumps(frame['o'])

    ws.send(json.dumps(frame))

def on_error(ws, error):
  print(error)
  on_close(ws)

def on_close(ws):

    ws.close()

def authenticate():
    global frame
    global user
    
    while True:
        try:

            frame['m'] = 0
            frame['i'] = 0
            frame['n'] = 'AuthenticateUser'
            frame['o'] =  user

            #websocket.enableTrace(True)
            ws = websocket.WebSocketApp(
                'wss://api.foxbit.com.br/',
                on_open = on_open,
                on_message = on_message,
                on_error = on_error,
                on_close = on_close
            )
            ws.run_forever()
        except Exception as e:
            print('Exception authenticate() - ', e, end='\r')
        
        time.sleep(3.154e+9)

def get_instruments():
    global frame
    
    with open("../instruments.log") as line:
        for data in line:
            data = data.replace("'", '"')
            data = json.loads(data)
            px = data['LastTradedPx']
            band(px,'u',2,1000)
            band(px,'m',2,1000)
            band(px,'l',2,1000)

    """
    while True:
        try:

            frame['m'] = 0
            frame['i'] = 0
            frame['n'] = 'GetInstruments'
            frame['o'] = {}

            #websocket.enableTrace(True)
            ws = websocket.WebSocketApp(
                "wss://api.foxbit.com.br/",
                on_open = on_open,
                on_message = on_message,
                on_error = on_error,
                on_close = on_close
            )
            ws.run_forever()
        except Exception as e:
            print('Exception get_instruments() - ', e, end='\r')
        time.sleep(3.154e+9)
    """

def statistics():
    global band_upper
    global band_medium
    global band_lower
    global last_traded_px
    global data_regression_base
    global len_regression_base

    while True:

        if len(band_upper) > 2:

            print('linear_regression(band_upper)')
            try:
                u = linear_regression(band_upper)

                a = data_regression_base[0]
                b = data_regression_base[1]

                
                c = u[0]
                d = u[1]

                xo = (d - b)/(a - c)

                f = u[0]*xo+u[1]
                g = data_regression_base[0]*xo+data_regression_base[1]
                h = len(band_upper)
                i = last_traded_px[-1]

                db = open('band_upper.log','w')
                db.write(f'{i};{f};{g};{h}\n')
                db.close()
            except Exception as e:
                pass

        if len(band_medium) > 2:
            print('linear_regression(band_medium)')

            try:
                u = linear_regression(band_medium)

                a = data_regression_base[0]
                b = data_regression_base[1]

                
                c = u[0]
                d = u[1]

                xo = (d - b)/(a - c)

                f = u[0]*xo+u[1]
                g = data_regression_base[0]*xo+data_regression_base[1]
                h = len(band_medium)
                i = last_traded_px[-1]

                db = open('band_medium.log','w')
                db.write(f'{i};{f};{g};{h}\n')
                db.close()

            except Exception as e:
                pass

        if len(band_lower) > 2:
            print('linear_regression(band_lower)')

            try:


                u = linear_regression(band_lower)

                a = data_regression_base[0]
                b = data_regression_base[1]

                
                c = u[0]
                d = u[1]

                xo = (d - b)/(a - c)

                f = u[0]*xo+u[1]
                g = data_regression_base[0]*xo+data_regression_base[1]
                h = len(band_lower)
                i = last_traded_px[-1]

                db = open('band_lower.log','w')
                db.write(f'{i};{f};{g};{h}\n')
                db.close()
            except Exception as e:
                pass

        time.sleep(1)

def regression_base():

    global data_regression_base
    global len_regression_base

    while True:

        now = datetime.now()

        time_start = int(datetime.timestamp(now-timedelta(days=30)))

        time_end = int(datetime.timestamp(now))

        request = requests.get("https://web-api.coinmarketcap.com/v1.1/cryptocurrency/quotes/historical?convert=USD,BTC,BRL&format=chart_crypto_details&id=1&interval=5m&time_end={time_end}&time_start={time_start}".format(time_end=time_end,time_start=time_start)).content

        request = json.loads(request)

        data = [];

        for i in request['data']:
            try:
                data.append(request['data'][i]['BRL'][0])
            except Exception as e:
                pass

        len_regression_base = len(data)

        data_regression_base = linear_regression(data)

        time.sleep(86400)

def main():
    #thread.start_new_thread(authenticate, ())
    thread.start_new_thread(regression_base, ())
    time.sleep(2)
    thread.start_new_thread(get_instruments, ())
    time.sleep(2)
    thread.start_new_thread(statistics, ())

    
    while True:
        time.sleep(3.154e+9)
        pass

if __name__ == '__main__':
    main()
