import requests
import time


class FreeForexRestApi:
    def __init__(self, queue):
        self.queue = queue
        self.URL = 'https://www.freeforexapi.com/api/live?pairs='
        self.prev_rate = None

    def start(self, order='USD', payment='KRW'):
        pair = order + payment
        while True:
            time.sleep(5)
            try:
                res = requests.get(self.URL, params={'pairs': pair})
                if res.status_code == 200:
                    msg = res.json()['rates'][pair]
                    timestamp = msg['timestamp']
                    rate = msg['rate']
                    if rate != self.prev_rate:
                        self.prev_rate = rate
                        self.on_message([timestamp, rate])
            except Exception:
                continue

    def on_message(self, message):
        if message == '':
            return
        # print(message)
        self.queue.put({"exchange": "freeforex", "message": message})


if __name__ == '__main__':
    from queue import Queue
    queue = Queue()
    FreeForexRestApi(queue).start()
