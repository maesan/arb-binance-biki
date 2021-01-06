import settings
from binance.client import Client
from binance.enums import *

import biki.rest_api as restapi

import time


def get_binance_ticker():
    client = Client(settings.KEYS['binance']['API'], settings.KEYS['binance']['SECRET'])
    ticker = client.get_ticker(symbol='BTCUSDT')
    res = {
        'sell': float(ticker['askPrice']),
        'buy': float(ticker['bidPrice'])
    }

    return res

def get_biki_ticker():
    restAPI = restapi.RestAPI(settings.KEYS['biki']['API'], settings.KEYS['biki']['SECRET'])
    ticker = restAPI.get_ticker('btcusdt')
    res = {
        'sell': ticker['data']['sell'],
        'buy': ticker['data']['buy']
    }

    return res

# 100 USDT で売り買いする
BUY_UNIT = 100.0

binance_client = Client(settings.KEYS['binance']['API'], settings.KEYS['binance']['SECRET'])
biki_client = restapi.RestAPI(settings.KEYS['biki']['API'], settings.KEYS['biki']['SECRET'])
while True:
    try:
        binance = get_binance_ticker()
        biki = get_biki_ticker()
        # 基準価格は全部の価格の平均としそこからの解離で判断する
        base = (biki['buy'] + biki['sell'] + binance['buy'] + binance['sell']) / 4.0
        diff1 = (biki['buy'] - binance['sell']) * 100 / base
        diff2 = (binance['buy'] - biki['sell']) * 100 / base

        diff = diff1
        if diff2 > diff1:
            diff = diff2
        
        if diff > 0.4:
            res_biki = None
            res_binance = None
            if diff1 > diff2:
                # BINANCEで買ってBIKIで売る
                buy_amount = BUY_UNIT / binance['sell']
                sell_amount = BUY_UNIT / biki['buy']
                res_binance = binance_client.create_order(
                    symbol="BTCUSDT",
                    side=SIDE_BUY,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=buy_amount,
                    price=str(binance['sell'])
                )
                res_biki = biki_client.create_order(
                    'btcusdt', 'limit', 'sell', sell_amount, biki['buy'])
                print('buy on BiKi')

            else:
                # BIKIで買ってBINANCEで売る
                buy_amount = BUY_UNIT / biki['sell']
                sell_amount = BUY_UNIT / binance['buy']
                res_binance = binance_client.create_order(
                    symbol="BTCUSDT",
                    side=SIDE_SELL,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=sell_amount,
                    price=str(binance['buy'])
                )
                res_biki = biki_client.create_order(
                    'btcusdt', 'limit', 'buy', buy_amount, biki['sell'])
                print('buy on BINANCE')

            print(res_binance)
            print(res_biki)
            with open('log.txt', 'a') as f:
                print(res_binance)
                print(res_biki)

        print('Biki: %f, %f'%(biki['buy'], biki['sell']))
        print('Bina: %f, %f'%(binance['buy'], binance['sell']))
        print(diff)
        with open('log.txt', 'a') as f:
            print(diff, file=f)
    except Exception as e:
        print(e)

    time.sleep(3)

    
