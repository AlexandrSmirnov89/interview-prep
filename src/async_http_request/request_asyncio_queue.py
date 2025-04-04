import json
import aiofiles
import aiohttp
import asyncio
from concurrent.futures import ProcessPoolExecutor
from asyncio import Semaphore, Queue


async def read_urls(file_urls: str, queue: Queue, num_worker: int):
    async with aiofiles.open(file_urls, 'r') as file:
        async for line in file:
            url = line.strip()
            if url:
                await queue.put(url)

    for _ in range(num_worker):
        await queue.put(None)

async def write_results(file_path: str, queue: Queue):
    async with aiofiles.open(file_path, 'a') as file:
        while True:
            result = await queue.get()
            if result is None:
                break

            await file.write(json.dumps(result, ensure_ascii=False) + '\n')
            queue.task_done()

async def get_response_and_write(
        url: str, session: aiohttp.ClientSession,
        semaphore: Semaphore,
        write_queue: Queue,
        pool: ProcessPoolExecutor
):
    async with semaphore:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    buffer = b''
                    async for chunk in response.content.iter_any():
                        buffer += chunk
                    loop = asyncio.get_running_loop()
                    content = await loop.run_in_executor(pool, json.loads, buffer.decode())
                    result = {'url': url, 'content': content}
                    await write_queue.put(result)

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f'Возникла ошибка при запросе {url}: {e}')

async def process_urls(
        url_queue: Queue,
        session: aiohttp.ClientSession,
        semaphore: Semaphore,
        write_queue: Queue,
        pool: ProcessPoolExecutor
):
    while True:
        url = await url_queue.get()
        if url is None:
            await write_queue.put(None)
            break
        await get_response_and_write(url, session, semaphore, write_queue, pool)

async def fetch_urls(file_urls, max_concurrent_requests = 5):
    semaphore: Semaphore = Semaphore(max_concurrent_requests)
    write_queue = Queue()
    url_queue = Queue()

    async with aiohttp.ClientSession() as session, ProcessPoolExecutor() as pool:

        reader_task = asyncio.create_task(read_urls(file_urls, url_queue, max_concurrent_requests))
        writer_task = asyncio.create_task(write_results('results.json', write_queue))

        download_tasks = []
        for _ in range(max_concurrent_requests):
            download_tasks.append(asyncio.create_task(process_urls(url_queue, session, semaphore, write_queue, pool)))

        await reader_task
        await asyncio.gather(*download_tasks)

        await writer_task
