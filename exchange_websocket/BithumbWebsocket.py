import websocket
import json


class BithumbWebsocket:
    def __init__(self, queue):
        self.queue = queue

    def start(self):
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://wss.bithumb.com/public",
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         header=["User-Agent: Mozilla/5.0\r\n"])
        while True:
            self.ws.run_forever()

    def on_open(self):
        print("### websocket open ###")
        self.ws.send(json.dumps({"currency": "BTC", "tickDuration": "24H", "service": "transaction"}))

    def on_message(self, message):
        if message == '':
            return
        # print(message)
        self.queue.put({"exchange": "bithumb", "message": message})

    def on_error(self, error):
        print("### websocket error ###" + error)

    def on_close(self):
        print("### websocket closed ###")
