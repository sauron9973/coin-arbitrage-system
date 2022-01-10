# -*- coding: utf-8 -*-

import math
from constant import *
import time


class BAR(object):
    def __init__(self, tick_second, tick_price, units):
        # BAR 생성 시각
        adjust_seconds = math.trunc(tick_second / units) * units
        self.start_time = self.end_time = adjust_seconds

        self.dirty = False

        self.open = self.high = self.low = self.close = tick_price

        self.windowHigh = tick_price
        self.windowLow = tick_price

        self.volumeShort = 0.0
        self.volumeLong = 0.0

        self.priceLong = tick_price
        self.priceShort = tick_price

        self.vpinLong = 0.0
        self.vpinShort = 0.0

        self.totalCnt = 0
        self.totalVolume = 0
        self.totalAmt = 0.0
        self.askCnt = 0
        self.bidCnt = 0
        self.askVolume = 0
        self.bidVolume = 0
        self.askAmt = 0.0
        self.bidAmt = 0.0

class CHART(object):
    def __init__(self, exchange, units=300):
        """ 차트 생성자 """

        self.exchange = exchange
        self.units = units
        self.longAlpha = 2.0 / (LONG_WINDOW_SIZE + 1.0)
        self.shortAlpha = 2.0 / (SHORT_WINDOW_SIZE + 1.0)

        self.candles = []

    def make_hist_bar(self, data):
        for bar in data:
            seconds = bar[0] / 1000
            open = bar[1]
            high = bar[2]
            low = bar[3]
            close = bar[4]
            volume = bar[5]
            if seconds == None or open == None or high == None or low == None or close == None or volume == None:
                continue

            self.create_bar(seconds, open)

            cur_candle = self.candles[-1]
            cur_candle.open = open
            cur_candle.close = close
            cur_candle.high = high
            cur_candle.low = low
            cur_candle.totalVolume = volume

        print(self.exchange, '마지막바 start_time:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.candles[-1].start_time)))

    def create_bar(self, tick_seconds, tick_price):
        """ BAR 생성 """

        new_candle = BAR(tick_seconds, tick_price, self.units)
        if len(self.candles) > 0:
            prev_candle = self.candles[-1]
            new_candle.volumeLong = (1 - self.longAlpha) * prev_candle.volumeLong + self.longAlpha * prev_candle.totalVolume
            new_candle.volumeShort = (1 - self.shortAlpha) * prev_candle.volumeShort + self.shortAlpha * prev_candle.totalVolume

            # window high, low
            for candle in self.candles[-12:]:
                if candle.low < new_candle.windowLow:
                    new_candle.windowLow = candle.low
                if candle.high > new_candle.windowHigh:
                    new_candle.windowHigh = candle.high

        self.candles.append(new_candle)

    def update_bar(self, tick_seconds, tick_price, tick_dir, tick_volume):
        """ 틱 업데이트 """

        # 최종 바 가져오기
        cur_candle = self.candles[-1]

        # 최종 시간 갱신
        cur_candle.end_time = tick_seconds

        # 고가, 저가 갱신
        if cur_candle.high < tick_price:
            cur_candle.high = tick_price
        if cur_candle.low > tick_price:
            cur_candle.low = tick_price

        # 종가 갱신
        cur_candle.close = tick_price

        # 거래량 갱신
        cur_candle.totalVolume += tick_volume
        cur_candle.totalAmt += tick_price * tick_volume
        cur_candle.totalCnt += 1
        if tick_dir == 1:
            cur_candle.askCnt += 1
            cur_candle.askVolume += tick_volume
            cur_candle.askAmt += tick_price * tick_volume
        else:
            cur_candle.bidCnt += 1
            cur_candle.bidVolume += tick_volume
            cur_candle.bidAmt += tick_price * tick_volume

        # 이전 바 가져오기
        if len(self.candles) > 2:
            prev_candle = self.candles[-2]

            # 이동평균 가격
            cur_candle.priceLong = (1 - self.longAlpha) * prev_candle.priceLong + self.longAlpha * cur_candle.close
            cur_candle.priceShort = (1 - self.shortAlpha) * prev_candle.priceShort + self.shortAlpha * cur_candle.close

            # VPIN
            cur_candle.vpinLong = (1 - self.longAlpha) * prev_candle.vpinLong + self.longAlpha * abs(cur_candle.askVolume - cur_candle.bidVolume)
            cur_candle.vpinShort = (1 - self.shortAlpha) * prev_candle.vpinShort + self.shortAlpha * abs(cur_candle.askVolume - cur_candle.bidVolume)
        else:
            # 이동평균 가격
            cur_candle.priceLong = cur_candle.close
            cur_candle.priceShort = cur_candle.close

            # VPIN
            cur_candle.vpinLong = abs(cur_candle.askVolume - cur_candle.bidVolume)
            cur_candle.vpinShort = abs(cur_candle.askVolume - cur_candle.bidVolume)

    def print_bar(self):
        cur_candle = self.candles[-1]

        print("exchange = %s, %d, vpin = %d, %d" %
                  (self.exchange, cur_candle.end_time, cur_candle.vpinLong, cur_candle.vpinShort))

    def make_bar(self, tick_seconds, tick_price, tick_dir, tick_volume):
        is_new = 0

        # 바 가 없으면 생성
        if len(self.candles) <= 0:
            self.create_bar(tick_seconds, tick_price)
            is_new = 1

        # 최종 바 가져오기
        cur_candle = self.candles[-1]

        # 신규 바 생성 조건
        if (tick_seconds - cur_candle.start_time) >= self.units:
            self.print_bar()

            # 신규 바 생성
            self.create_bar(tick_seconds, tick_price)
            is_new = 1

        # 틱 업데이트
        self.update_bar(tick_seconds, tick_price, tick_dir, tick_volume)

        return is_new
