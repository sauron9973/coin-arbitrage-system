from exchange_websocket.BitmexWebsocket import BitmexWebsocket
from exchange_websocket.UpbitWebsocket import UpbitWebsocket
from exchange_restapi.FreeForexRestApi import FreeForexRestApi
import multiprocessing as mp
from pathlib import Path
import datetime


def start_queue(queue, cls):
    queue_cls = cls(queue)
    queue_cls.start()


def run_crawler(cls, queue):
    proc = mp.Process(target=start_queue, args=(queue, cls))
    proc.start()


def crawl_and_save():
    KST = datetime.timezone(datetime.timedelta(hours=9))
    i = 0
    log_dir: Path = Path(__file__).parent / 'log'
    log_dir.mkdir(exist_ok=True)
    dt = datetime.datetime.now(KST).strftime("%Y-%m-%d %H%M%S")
    log_file = open(log_dir / f'{dt}.log', 'a')

    queue = mp.Queue()
    run_crawler(BitmexWebsocket, queue)
    run_crawler(UpbitWebsocket, queue)
    run_crawler(FreeForexRestApi, queue)

    while True:
        res = queue.get()
        log_file.write(f"{datetime.datetime.now(KST).strftime('%Y-%m-%d %H%M%S%f')},{res['exchange']},{res['message']}\n")
        if i == 100:
            log_file.flush()
            i = 0
        i += 1


if __name__ == '__main__':
    crawl_and_save()
