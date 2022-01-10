import websocket
import json


class UpbitWebsocket:
    def __init__(self, queue):
        self.queue = queue

    def start(self):
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        # while True:
        self.ws.run_forever()

    def on_open(self):
        print("### upbit websocket open ###")
        command = [{"ticket": "test"}, {"type": "trade", "codes": ["KRW-BTC"], "isOnlyRealtime": True},
                   {"type": "orderbook", "codes": ["KRW-BTC"], "isOnlyRealtime": True}]
        self.ws.send(json.dumps(command))

    def on_message(self, message):
        self.queue.put({"exchange": "upbit", "message": message})

    def on_error(self, error):
        print(error)
        print("### upbit websocket error ###")

    def on_close(self):
        print("### upbit websocket closed ###")
