# -*- coding: utf-8 -*-

import ccxt
import asyncio
import ccxt.async_support as ccxt_async


class Exchange(object):
    def __init__(self, logger, exchange_id, api_key, secret, timeout=30000, verbose=False, rate_limit=True):
        self.logger = logger
        self.api_key = api_key
        self.secret = secret
        self.timeout = timeout
        self.verbose = verbose
        self.rate_limit = rate_limit

        self.exchange = getattr(ccxt, exchange_id)({
            'apiKey': self.api_key,
            'secret': self.secret,
            'timeout': self.timeout,
            'enableRateLimit': self.rate_limit,
            'verbose': self.verbose,
            'options': {
                'adjustForTimeDifference': True,  # exchange-specific option
            }
        })

    def get_tickers(self):
        """
        전체 티커 조회

        :return:
            {
                'symbol': {
                    'symbol':        string symbol of the market ('BTC/USD', 'ETH/BTC', ...)
                    'info':        { the original non-modified unparsed reply from exchange API },
                    'timestamp':     int (64-bit Unix Timestamp in milliseconds since Epoch 1 Jan 1970)
                    'datetime':      ISO8601 datetime string with milliseconds
                    'high':          float, // highest price
                    'low':           float, // lowest price
                    'bid':           float, // current best bid (buy) price
                    'bidVolume':     float, // current best bid (buy) amount (may be missing or undefined)
                    'ask':           float, // current best ask (sell) price
                    'askVolume':     float, // current best ask (sell) amount (may be missing or undefined)
                    'vwap':          float, // volume weighed average price
                    'open':          float, // opening price
                    'close':         float, // price of last trade (closing price for current period)
                    'last':          float, // same as `close`, duplicated for convenience
                    'previousClose': float, // closing price for the previous period
                    'change':        float, // absolute change, `last - open`
                    'percentage':    float, // relative change, `(change/open) * 100`
                    'average':       float, // average price, `(last + open) / 2`
                    'baseVolume':    float, // volume of base currency traded for last 24 hours
                    'quoteVolume':   float, // volume of quote currency traded for last 24 hours
                },
                ...
            }
        """

        tickers = {}
        try:
            tickers = self.exchange.fetch_tickers(params={})
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return tickers

    def get_ticker(self, symbol):
        """
        티커 조회

        :param symbol: 심볼
        :return:
            {
                'symbol':        string symbol of the market ('BTC/USD', 'ETH/BTC', ...)
                'info':        { the original non-modified unparsed reply from exchange API },
                'timestamp':     int (64-bit Unix Timestamp in milliseconds since Epoch 1 Jan 1970)
                'datetime':      ISO8601 datetime string with milliseconds
                'high':          float, // highest price
                'low':           float, // lowest price
                'bid':           float, // current best bid (buy) price
                'bidVolume':     float, // current best bid (buy) amount (may be missing or undefined)
                'ask':           float, // current best ask (sell) price
                'askVolume':     float, // current best ask (sell) amount (may be missing or undefined)
                'vwap':          float, // volume weighed average price
                'open':          float, // opening price
                'close':         float, // price of last trade (closing price for current period)
                'last':          float, // same as `close`, duplicated for convenience
                'previousClose': float, // closing price for the previous period
                'change':        float, // absolute change, `last - open`
                'percentage':    float, // relative change, `(change/open) * 100`
                'average':       float, // average price, `(last + open) / 2`
                'baseVolume':    float, // volume of base currency traded for last 24 hours
                'quoteVolume':   float, // volume of quote currency traded for last 24 hours
            }
        """

        ticker = {}
        try:
            ticker = self.exchange.fetch_ticker(symbol, params={})
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return ticker

    def get_history_charts(self, symbol, timeframe, limit=400):
        """
        과거 가격 이력 조회 조회

        :param symbol: 심볼
        :param unit: 바 단위 (m, d, M)
        :return:
            [
                [
                    1504541580000, // UTC timestamp in milliseconds, integer
                    4235.4, // (O)pen price, float
                    4240.6, // (H)ighest price, float
                    4230.0, // (L)owest price, float
                    4230.7, // (C)losing price, float
                    37.72941911 // (V)olume (in terms of the base currency), float
                ],
                ...
            ]
        """

        bars = []
        try:
            since = self.exchange.milliseconds() - 86400000  # -1 day from now
            bars = self.exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=since, limit=limit,
                                             params={'partial': False, 'reverse': True})
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return bars

    def get_order_book(self, symbol, depth=10):
        """
        호가 조회

        :param symbol: 심볼
        :param depth: 호가 깊이
        :return:
            {
                'bids': [
                    [ price, amount ], // [ float, float ]
                    [ price, amount ],
                    ...
                ],
                'asks': [
                    [ price, amount ],
                    [ price, amount ],
                    ...
                ],
                'timestamp': 1499280391811, // Unix Timestamp in milliseconds (seconds * 1000)
                'datetime': '2017-07-05T18:47:14.692Z', // ISO8601 datetime string with milliseconds
            }
        """

        order_book = {}
        try:
            order_book = self.exchange.fetch_order_book(symbol, depth, params={})
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return order_book

    def get_trades(self, symbol):
        """
        거래정보 조회

        :param symbol: 심볼
        :return:
            [
                {
                    'info':       { ... },                  // the original decoded JSON as is
                    'id':        '12345-67890:09876/54321', // string trade id
                    'timestamp':  1502962946216,            // Unix timestamp in milliseconds
                    'datetime':  '2017-08-17 12:42:48.000', // ISO8601 datetime with milliseconds
                    'symbol':    'ETH/BTC',                 // symbol
                    'order':     '12345-67890:09876/54321', // string order id or undefined/None/null
                    'type':      'limit',                   // order type, 'market', 'limit' or undefined/None/null
                    'side':      'buy',                     // direction of the trade, 'buy' or 'sell'
                    'price':      0.06917684,               // float price in quote currency
                    'amount':     1.5,                      // amount of base currency
                },
                ...
            ]
        """

        trades = []
        try:
            trades = self.exchange.fetch_tickers(symbol, params={})
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return trades

    def get_balance(self):
        """
        잔고 조회

        :return:
            {
                'info':  { ... },    // the original untouched non-parsed reply with details

                //-------------------------------------------------------------------------
                // indexed by availability of funds first, then by currency

                'free':  {           // money, available for trading, by currency
                    'BTC': 321.00,   // floats...
                    'USD': 123.00,
                    ...
                },

                'used':  { ... },    // money on hold, locked, frozen, or pending, by currency

                'total': { ... },    // total (free + used), by currency

                //-------------------------------------------------------------------------
                // indexed by currency first, then by availability of funds

                'BTC':   {           // string, three-letter currency code, uppercase
                    'free': 321.00   // float, money available for trading
                    'used': 234.00,  // float, money on hold, locked, frozen or pending
                    'total': 555.00, // float, total balance (free + used)
                },

                'USD':   {           // ...
                    'free': 123.00   // ...
                    'used': 456.00,
                    'total': 579.00,
                },

                ...
            }
        """

        balance = {}
        try:
            balance = self.exchange.fetch_balance(params={})
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return balance

    def purge_cached_orders(self, before_hour):
        """
        사용하지 않는 주문 제거

        :param before_hour: 기준시각
        :return: 없음
        """

        try:
            before = self.exchange.milliseconds() - before_hour * 60 * 60 * 1000
            self.exchange.purge_cached_orders(before)
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)

    def buy_limit_order(self, symbol, qty, price):
        """
        지정가 매수

        :param symbol: 심볼
        :param qty: 수량
        :param price: 가격
        :return:
            {
              "id": "7378568",
              "datetime": "2018-04-03T12:55:37.805Z",
              "timestamp": 1522760136805,
              "status": "open",
              "symbol": "MONA/JPY",
              "type": "limit",
              "side": "buy",
              "price": 2000.0,
              "cost": 0.0,
              "amount": 1.0,
              "filled": 0.0,
              "remaining": 1.0,
              "trades": null,
              "fee": null,
              "info": {
                "order_id": 7378568,
                "pair": "mona_jpy",
                "side": "buy",
                "type": "limit",
                "start_amount": "1.00000000",
                "remaining_amount": "1.00000000",
                "executed_amount": "0.00000000",
                "price": "2000.0000",
                "average_price": "0.0000",
                "ordered_at": 1522760136805,
                "status": "UNFILLED"
              }
            }
        """

        order = {}
        try:
            order = self.exchange.create_limit_buy_order(symbol, qty, price)
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return order

    def sell_limit_order(self, symbol, qty, price):
        """
        지정가 매도

        :param symbol: 심볼
        :param qty: 수량
        :param price: 가격
        :return:
            {
              "id": "7378568",
              "datetime": "2018-04-03T12:55:37.805Z",
              "timestamp": 1522760136805,
              "status": "open",
              "symbol": "MONA/JPY",
              "type": "limit",
              "side": "sell",
              "price": 2000.0,
              "cost": 0.0,
              "amount": 1.0,
              "filled": 0.0,
              "remaining": 1.0,
              "trades": null,
              "fee": null,
              "info": {
                "order_id": 7378568,
                "pair": "mona_jpy",
                "side": "sell",
                "type": "limit",
                "start_amount": "1.00000000",
                "remaining_amount": "1.00000000",
                "executed_amount": "0.00000000",
                "price": "2000.0000",
                "average_price": "0.0000",
                "ordered_at": 1522760136805,
                "status": "UNFILLED"
              }
            }
        """

        order = {}
        try:
            order = self.exchange.create_limit_sell_order(symbol, qty, price)
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return order

    def buy_market_order(self, symbol, qty):
        """
        시장가 매수

        :param symbol: 심볼
        :param qty: 수량
        :return:
            {
              "id": "379751834",
              "datetime": "2018-04-03T17:02:40.871Z",
              "timestamp": 1522774959871,
              "status": "open",
              "symbol": "BTC/JPY",
              "type": "market",
              "side": "buy",
              "price": 0.0,
              "cost": 0.0,
              "amount": 0.0001,
              "filled": 0.0,
              "remaining": 0.0001,
              "trades": null,
              "fee": null,
              "info": {
                "order_id": 379751834,
                "pair": "btc_jpy",
                "side": "buy",
                "type": "market",
                "start_amount": "0.00010000",
                "remaining_amount": "0.00010000",
                "executed_amount": "0.00000000",
                "average_price": "0.0000",
                "ordered_at": 1522774959871,
                "status": "UNFILLED"
              }
            }
        """

        order = {}
        try:
            order = self.exchange.create_market_buy_order(symbol, qty)
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return order

    def sell_market_order(self, symbol, qty):
        """
        시장가 매도

        :param symbol: 심볼
        :param qty: 수량
        :return:
            {
              "id": "7378542",
              "datetime": "2018-04-03T12:54:55.633Z",
              "timestamp": 1522760094633,
              "status": "open",
              "symbol": "MONA/JPY",
              "type": "limit",
              "side": "sell",
              "price": 2000.0,
              "cost": 0.0,
              "amount": 1.0,
              "filled": 0.0,
              "remaining": 1.0,
              "trades": null,
              "fee": null,
              "info": {
                "order_id": 7378542,
                "pair": "mona_jpy",
                "side": "sell",
                "type": "limit",
                "start_amount": "1.00000000",
                "remaining_amount": "1.00000000",
                "executed_amount": "0.00000000",
                "price": "2000.0000",
                "average_price": "0.0000",
                "ordered_at": 1522760094633,
                "status": "UNFILLED"
              }
            }
        """

        order = {}
        try:
            order = self.exchange.create_market_sell_order(symbol, qty)
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return order

    def get_open_orders(self, symbol):
        """
        열려져 있는 주문 리스트 조회

        :param symbol: 심볼
        :return:
        """

        orders = []
        try:
            orders = self.exchange.fetch_open_orders(symbol)
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return orders

    def get_order_status(self, order_id, symbol):
        """
        주문 상태 조회

        :param order_id: 주문번호
        :param symbol: 심볼
        :return:
            {
                'id':                '12345-67890:09876/54321', // string
                'datetime':          '2017-08-17 12:42:48.000', // ISO8601 datetime of 'timestamp' with milliseconds
                'timestamp':          1502962946216, // order placing/opening Unix timestamp in milliseconds
                'lastTradeTimestamp': 1502962956216, // Unix timestamp of the most recent trade on this order
                'status':     'open',         // 'open', 'closed', 'canceled'
                'symbol':     'ETH/BTC',      // symbol
                'type':       'limit',        // 'market', 'limit'
                'side':       'buy',          // 'buy', 'sell'
                'price':       0.06917684,    // float price in quote currency
                'amount':      1.5,           // ordered amount of base currency
                'filled':      1.1,           // filled amount of base currency
                'remaining':   0.4,           // remaining amount to fill
                'cost':        0.076094524,   // 'filled' * 'price' (filling price used where available)
                'trades':    [ ... ],         // a list of order trades/executions
                'fee': {                      // fee info, if available
                    'currency': 'BTC',        // which currency the fee is (usually quote)
                    'cost': 0.0009,           // the fee amount in that currency
                    'rate': 0.002,            // the fee rate (if available)
                },
                'info': { ... },              // the original unparsed order structure as is
            }
        """

        order = {}
        try:
            # order = asyncio.get_event_loop().run_until_complete(self.exchange.fetch_order(order_id, symbol))
            order = self.exchange.fetch_order(order_id, symbol)
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return order

    def cancel_order(self, order_id, symbol):
        """
        주문 취소

        :param order_id: 주문번호
        :param symbol: 심볼
        :return:
            {
              "order_id": 7365912,
              "pair": "mona_jpy",
              "side": "sell",
              "type": "limit",
              "start_amount": "1.00000000",
              "remaining_amount": "1.00000000",
              "executed_amount": "0.00000000",
              "price": "1000.0000",
              "average_price": "0.0000",
              "ordered_at": 1522744451311,
              "canceled_at": 1522758207410,
              "status": "CANCELED_UNFILLED"
            }
        """

        order = {}
        try:
            order = self.cancel_order(order_id, symbol)
        except (ccxt.ExchangeError, ccxt.NetworkError) as error:
            resp = {}
            self.logger.error(" [*] Got an Error", type(error).__name__, error.args)
        return order
