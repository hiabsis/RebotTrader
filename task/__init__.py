import aiohttp
import asyncio

concurrent = 5
url = 'https://www.baidu.com'
session = None
semaphore = asyncio.Semaphore(concurrent)


async def scrape_api(i):
    async with semaphore:
        print('爬取', url, i)
        async with session.get(url) as resp:
            await asyncio.sleep(1)
            return await resp.text()


async def main():
    global session
    session = aiohttp.ClientSession()
    tasks = [asyncio.ensure_future(scrape_api(i)) for i in range(1, 10001)]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
