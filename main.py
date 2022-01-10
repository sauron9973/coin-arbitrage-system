# -*- coding: utf-8 -*-

import logging.handlers
import time
from exchange_restapi import FreeForexRestApi
from exchange_websocket import UpbitWebsocket, BitmexWebsocket
from exchange import Exchange
import multiprocessing as mp
import json
from constant import *
from trader import Trader

logger = logging.getLogger('arbitrage')
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler('./log/my.log')
streamHandler = logging.StreamHandler()
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

queue = mp.Queue()


def start_queue(queue, cls):
    queue_cls = cls(queue)
    queue_cls.start()


if __name__ == "__main__":
    upbit_exchange = Exchange(logger, 'upbit', UPBIT_API_KEY, UPBIT_SECRET, 30000, False, True)
    bitmex_exchange = Exchange(logger, 'bitmex', BITMEX_API_KEY, BITMEX_SECRET, 30000, True, True)

    trader = Trader(l_exchange=upbit_exchange, s_exchange=bitmex_exchange)
    # Todo 장부 정보 먼저 가져오기
    trader.neutralize_position()
    trader.init_hist_chart()

    for cls in [UpbitWebsocket.UpbitWebsocket, BitmexWebsocket.BitmexWebsocket, FreeForexRestApi.FreeForexRestApi]:
        process_cls = mp.Process(target=start_queue, args=(queue, cls))
        process_cls.start()

    while True:
        message = queue.get()
        exchange = message['exchange']
        if exchange == 'bitmex':  # 비트맥스인 경우
            parsed_msg = json.loads(message['message'])
            if 'table' in parsed_msg:
                if parsed_msg['table'] == 'trade' and parsed_msg['action'] == 'insert':  # 체결정보인 경우
                    for tick in parsed_msg['data']:
                        # 거래시간
                        tick_seconds = time.time()

                        # 거래량
                        tick_dir = 1 if tick['side'] == 'Buy' else -1
                        tick_volume = float(tick['size'])

                        # 거래가격
                        tick_price = float(tick['price'])
                        # print(exchange, tick_seconds, tick_price, tick_dir, tick_volume)
                        trader.make_bars(tick_seconds, tick_price, tick_dir, tick_volume, 'short')

                if parsed_msg['table'] == 'orderBookL2_25':  # 호가인 경우
                    pass

        if exchange == 'upbit':  # 업비트인 경우
            parsed_msg = json.loads(message['message'])
            if parsed_msg['type'] == 'trade':  # 체결정보인 경우
                # 거래시간
                tick_seconds = time.time()

                # 거래량
                tick_dir = 1 if parsed_msg['ask_bid'] == 'ASK' else -1
                tick_volume = float(parsed_msg['trade_volume'])

                # 거래가격
                tick_price = float(parsed_msg['trade_price'])
                # print(exchange, tick_seconds, tick_price, tick_dir, tick_volume)
                trader.make_bars(tick_seconds, tick_price, tick_dir, tick_volume, 'long')

            if (parsed_msg['type'] == 'orderbook'):  # 호가인 경우
                pass
        if exchange == 'freeforex':  # freeForex인 경우
            parsed_msg = message['message']
            # 거래시간
            tick_seconds = parsed_msg[0]

            # 거래량
            tick_dir = 1  # 항상 Buy로 설정
            tick_volume = 1  # 항상 1로 설정

            # 거래가격
            tick_price = parsed_msg[1]
            trader.make_bars(tick_seconds, tick_price, tick_dir, tick_volume, 'benchmark')
