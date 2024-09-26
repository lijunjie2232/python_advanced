import asyncio
from collections.abc import Generator, Coroutine
import time
from pathlib import Path
from sys import executable
from shutil import rmtree
from random import randint
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool
from itertools import repeat


async def mylogger(log, delay=0):
    if delay:
        await asyncio.sleep(delay)
    print("log: %s" % log)
    return log


async def runServer():
    await asyncio.ensure_future(myserver())


async def myserver():
    print("server start")
    await asyncio.sleep(2)
    print("server stop")


async def mycoroutine():
    await asyncio.sleep(1)
    return "mycoroutine finished"


def mycallback(fut):
    print(f"future result is: {fut.result()}")


async def myFutureSet(fut):
    fut.set_result("future done")


async def mywriter(file, content, mode="w", *args, **kwargs):
    with open(file, mode, *args, **kwargs) as f:
        f.write(content)


def mywriterSnyc(file, content, mode="w", *args, **kwargs):
    with open(file, mode, *args, **kwargs) as f:
        f.write(content)


if __name__ == "__main__":

    ### coroutine
    print(asyncio.__all__)
    l = mylogger("print log")
    print(l)

    print(type(l))
    print(isinstance(l, Coroutine))
    print(isinstance(l, Generator))

    myloop = asyncio.get_event_loop()
    asyncio.set_event_loop(myloop)
    print(myloop)

    # run coroutine with loop
    mytask = myloop.create_task(l)
    myloop.run_until_complete(mytask)

    # run coroutine with asyncio.run
    asyncio.run(mylogger("print log2"))

    # run mycoroutine with ensure_task
    asyncio.run(runServer())

    # task result
    mytask = myloop.create_task(mycoroutine())
    myloop.run_until_complete(mytask)
    print(mytask.result())

    # run with callback && task result
    mytask = myloop.create_task(mycoroutine())
    mytask.add_done_callback(mycallback)
    myloop.run_until_complete(mytask)

    # use future to run task
    myloop = asyncio.new_event_loop()
    asyncio.set_event_loop(myloop)
    fut = asyncio.Future()
    print(fut)
    print(fut.done())
    myloop.create_task(myFutureSet(fut))
    myloop.run_until_complete(fut)
    print(fut.done())
    print(fut.result())

    print("**********concurency with asyncio.wait**********")
    start = time.time()
    msgs = [mylogger("massage %d" % i, 1) for i in range(10)]
    mytasks = [asyncio.ensure_future(i) for i in msgs]
    myloop.run_until_complete(asyncio.wait(mytasks))
    end = time.time()
    for i in mytasks:
        print(i.result())
    print(f"use time: {end - start} ms")

    print("**********concurency with asyncio.gather**********")
    start = time.time()
    msgs = [mylogger("massage %d" % i, 1) for i in range(10)]
    mytasks = [asyncio.ensure_future(i) for i in msgs]
    myloop.run_until_complete(asyncio.gather(*mytasks))
    end = time.time()
    for i in mytasks:
        print(i.result())
    print(f"use time: {end - start} ms")

    print("**********concurency file writer with coroutine**********")
    ROOT = Path(__file__).parent.absolute()
    if Path(__file__).suffix == ".exe":
        ROOT = Path(executable).parent.absolute()
    TEMP = ROOT / "tmp"
    TEMP.mkdir(exist_ok=True)
    filename = "randomfile_%s.txt"
    start = time.time()
    msgs = [
        mywriter(
            TEMP / (filename % str(i).rjust(5, "0")),
            "random: %d" % randint(0, 9999999),
            "w",
            encoding="utf-8",
        )
        for i in range(10000)
    ]
    mytasks = [asyncio.ensure_future(i) for i in msgs]
    myloop.run_until_complete(asyncio.gather(*mytasks))
    end = time.time()
    print(f"use time: {end - start} ms")
    rmtree(TEMP)

    print("**********concurency file writer with threadpoolexecutor**********")
    ROOT = Path(__file__).parent.absolute()
    if Path(__file__).suffix == ".exe":
        ROOT = Path(executable).parent.absolute()
    TEMP = ROOT / "tmp"
    TEMP.mkdir(exist_ok=True)
    filename = "randomfile_%s.txt"
    start = time.time()
    threadPool = ThreadPoolExecutor(32)
    for i in range(10000):
        threadPool.submit(
            mywriterSnyc,
            TEMP / (filename % str(i).rjust(5, "0")),
            "random: %d" % randint(0, 9999999),
            "w",
            encoding="utf-8",
        )

    threadPool.shutdown()

    end = time.time()
    print(f"use time: {end - start} ms")
    rmtree(TEMP)

    print("**********concurency file writer with threadpoolexecutor**********")
    ROOT = Path(__file__).parent.absolute()
    if Path(__file__).suffix == ".exe":
        ROOT = Path(executable).parent.absolute()
    TEMP = ROOT / "tmp"
    TEMP.mkdir(exist_ok=True)
    filename = "randomfile_%s.txt"
    start = time.time()
    threadPool = ThreadPool(32)

    for i in range(10000):
        threadPool.apply_async(
            mywriterSnyc,
            args=(
                TEMP / (filename % str(i).rjust(5, "0")),
                "random: %d" % randint(0, 9999999),
                "w",
            ),
            kwds={"encoding": "utf-8"},
        )
    threadPool.close()
    threadPool.join()
    end = time.time()
    print(f"use time: {end - start} ms")
    rmtree(TEMP)

    pass
