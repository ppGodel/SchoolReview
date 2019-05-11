import random
import asyncio

import rx
from rx import of, operators as op, Observable, create
from rx.core import Observer, typing


async def send_request_to(url, observer):
    process_time = random.randint(0, 10)
    print("send request {}, will wait {} seconds".format(url, process_time))
    await asyncio.sleep(process_time)
    observer.on_next({"url": url, "time": process_time})


async def async_sender(urls, observer):
    tasks = []
    for url in urls:
        tasks.append(asyncio.ensure_future(send_request_to(url, observer)))
    await asyncio.gather(*tasks)


def rx_url_loop(urls):
    def rx_loop(observer: Observer, scheduler: typing.Scheduler):
        print("Looping urls")
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(async_sender(urls, observer))
        except Exception as e:
            observer.on_error(e)
        finally:
            loop.close()
            observer.on_completed()

    return rx_loop


class RxAsyncRequest(Observer):
    def __init__(self):
        self.tasks = []

    def on_next(self, value):
        print("State changed! a event has been received")
        print(value)

    def on_completed(self):
        print("Finished")

    def on_error(self, error):
        print("Error: {}".format(error))


some_urls = ["google", "youtube", "twitter", "stackoverflow", "localhost"]
print("urls in order to be queried")
print(some_urls)
source = rx.create(rx_url_loop(some_urls))

source.pipe(op.filter(lambda x: x.get("time") % 2 == 0),
    op.map(lambda x: {"url": x.get("url").upper(), "time": x.get("time")}),
    op.map(lambda x: "Received: {0}, has successfully completed after {1} seconds"
              .format(x.get("url"), x.get("time")))).subscribe(RxAsyncRequest())


# other_urls = ["yahoo", "vk", "instagram", "reddit", "noip"]
# print(other_urls)
# source2 = of(*other_urls)
# source2.pipe(
#     op.map(lambda s: len(s)),
#     op.filter(lambda s: s > 5)
# ).subscribe(RxAsyncRequest())
