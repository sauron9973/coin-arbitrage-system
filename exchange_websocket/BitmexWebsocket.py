import websocket
import json


class BitmexWebsocket:
    def __init__(self, queue):
        self.queue = queue

    def start(self):
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://www.bitmex.com/realtime",
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        # while True:
        self.ws.run_forever()

    def on_open(self):
        print("### bitmex websocket open ###")
        command = {"op": "subscribe", "args": ["orderBookL2_25:XBTUSD", "trade:XBTUSD"]}
        self.ws.send(json.dumps(command))

    def on_message(self, message):
        self.queue.put({"exchange": "bitmex", "message": message})

    def on_error(self, error):
        print(error)
        print("### bitmex websocket error ###")

    def on_close(self):
        print("### bitmex websocket closed ###")


