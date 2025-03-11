import csv
import random
from multiprocessing import Pool, Process, Queue
import time
import functools

import concurrent.futures


def measure_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        function_name = func.__name__
        size_list = args[0]
        with open('performance_results.csv', 'a', newline='') as csvfile:
            columns = []
            writer = csv.writer(csvfile)
            writer.writerow([function_name, size_list, f"{execution_time:.4f}"])
        print(f"Функция {func.__name__} выполнилась за {execution_time:.4f} секунд")
        return result
    return wrapper


def generate_data(n: int):
    result = [random.randrange(1, 1000) for _ in range(n)]
    return result

def process_number(n: int):
    if n < 0:
        return None

    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

@measure_time
def single_threaded(size_list):
    random_list = generate_data(size_list)
    for n in random_list:
        process_number(n)

    return random_list

@measure_time
def tread_pool(size_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for n in generate_data(size_list):
            executor.submit(process_number, n)

@measure_time
def multiprocess_pool(size_list):
    with Pool(processes=2) as pool:
        for n in generate_data(size_list):
            pool.apply_async(process_number, (n, ))

@measure_time
def multiprocess_queue(size_list):
    data_size = size_list
    workers_count = 4
    data_queue = Queue()
    result_queue = Queue()
    workers_list = []

    for _ in range(workers_count):
        process = Process(target=worker, args=(data_queue, result_queue))
        workers_list.append(process)
        process.start()

    data = generate_data(data_size)
    for item in data:
        data_queue.put(item)

    for _ in range(workers_count):
        data_queue.put(None)

    results = []
    for _ in range(data_size):
        results.append(result_queue.get())

    for process in workers_list:
        process.join()

    return results


def worker(data_queue, result_queue):
    while True:
        item = data_queue.get()
        if item is None:
            break
        result = process_number(item)
        result_queue.put(result)


if __name__ == '__main__':
    with open('performance_results.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Function Name', 'Data Size', 'Execution Time (s)'])
    single_threaded(1_000_000)
    tread_pool(1_000_000)
    multiprocess_pool(1_000_000)
    multiprocess_queue(1_000_000)
