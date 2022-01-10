from chart import CHART
from constant import *

import numpy as np
from portfolio import Portfolio
import time

class Trader:
    def __init__(self, l_exchange, s_exchange):
        self.portfolio = Portfolio
        self.l_exchange = l_exchange  # Long 거래소
        self.s_exchange = s_exchange  # Short 거래소

        self.l_chart = CHART(exchange=LONG_EXCHANGE, units=CHART_UNITS)  # LONG 차트
        self.s_chart = CHART(exchange=SHORT_EXCHANGE, units=CHART_UNITS)  # SHORT 차트
        self.b_chart = CHART(exchange=BENCHMARK, units=CHART_UNITS)  # 벤치마크 차트
        self.p_chart = CHART(exchange='{}/{}'.format(LONG_EXCHANGE, SHORT_EXCHANGE), units=CHART_UNITS)  # PAIR 차트

        self.benchmark = None  # 벤치마크
        self.entry_point = None  # 포지션 진입점
        self.exit_point = None  # 포지션 청산점
        self.balance_point = None  # 포지션 균형점
        self.current_point = None  # 현재 지점

        self.bb_exit_band = None
        self.bb_entry_band = None
        self.adj_entry_benchmark = None

    def neutralize_position(self, auto=False):
        """
        체크 : (롱 주문 없음 AND 숏 -1x 레버리지)

        :param auto: Neutralized Position이 아니면 자동 조정
        :return:

        l_open_orders = self.l_exchange.open_orders('BTC/KRW')
        s_open_orders = self.s_exchange.open_orders('BTC/USD')

        ~
        """
        pass

    def init_hist_chart(self):
        # 페어 데이터 합성
        l_hist_bars = self.l_exchange.get_history_charts(BTC_KRW_TICKER, BAR_INTERVAL)
        s_hist_bars = self.s_exchange.get_history_charts(BTC_USD_TICKER, BAR_INTERVAL)
        p_hist_bars = []

        min_length = min([len(l_hist_bars), len(s_hist_bars)])
        for i in reversed(range(1, min_length+1)):
            l_element = l_hist_bars[-i]
            s_element = s_hist_bars[-i]
            s_element[0] -= 5 * 60 * 1000
            
            p_element = [l_element[0], l_element[1] / s_element[1], l_element[2] / s_element[2],
                             l_element[3] / s_element[3], l_element[4] / s_element[4], l_element[5] / s_element[5]]
            p_hist_bars.append(p_element)

        self.l_chart.make_hist_bar(data=l_hist_bars)
        self.s_chart.make_hist_bar(data=s_hist_bars)
        self.p_chart.make_hist_bar(data=p_hist_bars)

    def update_points(self):
        # 새로운 바가 생성되었을 때 업데이트
        # WINDOW_SIZE 볼린저 밴드 생성
        window_candles = [candle.close for candle in self.p_chart.candles[-LONG_WINDOW_SIZE:]]
        self.balance_point = np.average(window_candles)
        std = np.std(window_candles)

        # MIN(볼린저 하단밴드, 기준환율 + 조정)
        self.bb_entry_band = self.balance_point + K_ENTRY_POINT * std
        self.bb_exit_band = self.balance_point + K_EXIT_POINT * std

        # 환율 + DISCOUNTED_VALUE (Default - ENTRY: 10, EXIT: 0)
        self.adj_entry_benchmark = self.b_chart.candles[-1].close + ENTRY_PREMIUM_VALUE
        self.adj_exit_benchmark = self.b_chart.candles[-1].close + EXIT_PREMIUM_VALUE

        self.entry_point = min(self.bb_entry_band, self.adj_entry_benchmark)  # MIN(1186, 1170+10) = 1180
        self.exit_point = max(self.bb_exit_band, self.adj_exit_benchmark)  # MAX(1196, 1170) = 1196

    # 차트 업데이트
    def make_bars(self, tick_seconds, tick_price, tick_dir, tick_volume, side):
        if side == 'long':
            self.l_chart.make_bar(tick_seconds, tick_price, tick_dir, tick_volume)
        elif side == 'short':
            self.s_chart.make_bar(tick_seconds, tick_price, tick_dir, tick_volume)
        else:
            self.b_chart.make_bar(tick_seconds, tick_price, tick_dir, tick_volume)

        # 롱숏, 벤치마크바 가 없으면 종료
        if len(self.l_chart.candles) <= 0 or len(self.s_chart.candles) <= 0 or len(self.b_chart.candles) <= 0:
            return 0

        # 롱숏, 벤치마크바 가 있으면 페어 바 업데이트
        else:
            l_candle = self.l_chart.candles[-1]
            s_candle = self.s_chart.candles[-1]
            self.current_point = l_candle.close / s_candle.close

            # 페어 바 업데이트
            is_new = self.p_chart.make_bar(tick_seconds, self.current_point, 1,
                                           l_candle.totalVolume / s_candle.totalVolume)
            if is_new:
                # TODO : 트래픽이 많을 수 있음
                self.update_points()
                print(" [*] Current: %.3f, Entry : %.3f, Exit : %.3f, Bband-Entry: %.3f, Bband-Exit: %.3f, Benchmark-Entry: %.3f, Benchmark-Exit: %.3f" % (
                        self.current_point, self.entry_point, self.exit_point, self.bb_entry_band, self.bb_exit_band,
                        self.adj_entry_benchmark, self.adj_exit_benchmark))

            return is_new

    def check_signal(self):
        """
        :return: 1: open, 0: neutral, -1: close
        """
        return 1

    def open_position(self, split=1):
        pass

    def close_position(self):
        pass
