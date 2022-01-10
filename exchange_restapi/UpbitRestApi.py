import requests
import json
import time


class UpbitRestApi:
    def get_hist_bar_data(self, minute=5, bar_num=200):
        URL = 'https://crix-api-cdn.upbit.com/v1/crix/candles/minutes/%s?code=CRIX.UPBIT.KRW-BTC&count=%s&ciqrandom=1563101897538' % (
            minute, bar_num)
        res = requests.get(URL)
        chart_data = json.loads(res.text)
        ret = []
        for bar in reversed(chart_data):
            seconds = int(bar['timestamp']) / 1000
            open = float(bar['openingPrice'])
            close = float(bar['tradePrice'])
            high = float(bar['highPrice'])
            low = float(bar['lowPrice'])
            volume = float(bar['candleAccTradeVolume'])
            ret.append([seconds, open, high, low, close, volume])

        return ret
