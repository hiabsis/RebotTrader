# python 源码
import asyncio
import time


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)


async def main():
    task1 = asyncio.create_task(
        say_after(1, 'hello'))

    task2 = asyncio.create_task(
        say_after(3, 'world'))

    print(f"started at {time.strftime('%X')}")

    # Wait until both tasks are completed (should take around 2 seconds.)
    # 两个任务同时执行，直到到所有任务执行完成。
    await task1
    await task2

    print(f"finished at {time.strftime('%X')}")


