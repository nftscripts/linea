from typing import Awaitable
import random
import copy

from loguru import logger
from tqdm import tqdm

from asyncio import (
    AbstractEventLoop,
    get_event_loop,
    create_task,
    Semaphore,
    gather,
    sleep,
)

from src.utils.mappings import module_handlers
from config import *

from src.utils.helper import (
    private_keys,
    active_module,
)


async def process_private_key(private_key: str, pbar: tqdm, thread_num: int, semaphore: Semaphore) -> bool:
    tasks = []
    if RANDOMIZE is True:
        modules = copy.copy(active_module)
        random.shuffle(modules)
    else:
        modules = active_module
    async with semaphore:
        for pattern in modules:
            task = create_task(module_handlers[pattern](private_key, pbar))
            tasks.append(task)
            time_to_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
            logger.info(f'Thread {thread_num}: Sleeping {time_to_sleep} seconds...')
            await sleep(time_to_sleep)
            await task
        await gather(*tasks)
    return all(task.done() for task in tasks)


async def main(loop: AbstractEventLoop) -> None:
    num_threads = min(NUM_THREADS, len(private_keys))
    semaphore = Semaphore(num_threads)
    if not RUN_FOREVER:
        tasks = []
        thread_num = 1
        for private_key in private_keys:
            task = loop.create_task(process_private_key(private_key, pbar, thread_num, semaphore))
            tasks.append(task)
            thread_num += 1
        await gather(*tasks)
        completed = {private_key: task_result for private_key, task_result in zip(private_keys, tasks)}
        if all(completed.values()):
            return
    while RUN_FOREVER:
        tasks = []
        thread_num = 1
        for private_key in private_keys:
            task = loop.create_task(process_private_key(private_key, pbar, thread_num, semaphore))
            tasks.append(task)
            thread_num += 1
        await gather(*tasks)


def start_event_loop(awaitable: Awaitable[object], loop: AbstractEventLoop) -> None:
    loop.run_until_complete(awaitable)


if __name__ == '__main__':
    with tqdm(total=len(private_keys)) as pbar:
        async def tracked_main():
            await main(get_event_loop())
        start_event_loop(tracked_main(), get_event_loop())
        pbar.close()
