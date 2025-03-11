import json

import aiofiles
import aiohttp
import asyncio
from asyncio import Semaphore


async def get_url_and_write(url: str, session: aiohttp.ClientSession, semaphore: Semaphore, file):
    async with semaphore:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    buffer = b''
                    async for chunk in response.content.iter_any():
                        buffer += chunk
                    result = {'url': url, 'content': json.loads(buffer.decode())}
                    await file.write(json.dumps(result, ensure_ascii=False) + '\n')
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f'Возникла ошибка {url} при запросе: {e}')

async def fetch_urls(file_urls):
    semaphore: Semaphore = Semaphore(5)

    async with aiofiles.open(file_urls, 'r') as file:
        data_urls = [line.strip() for line in await file.readlines() if line.strip()]

    async with aiohttp.ClientSession() as session, aiofiles.open('results.json', 'a') as file:
        tasks = [asyncio.create_task(get_url_and_write(url, session, semaphore, file))
                 for url in data_urls]
        await asyncio.gather(*tasks)
