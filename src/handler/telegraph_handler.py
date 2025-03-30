import asyncio

from src.logger import logger
from telegram import Update

import src.config as config
from src.task import TelegraphTask
from src.dialog import Dialog


class TelegraphHandler:
    def __init__(self):
        self._task_queue = asyncio.Queue()
        self._idle_counter = 0
        self._loop_wakeup = asyncio.Event()
        self._main_loop_task = None

    async def start_loop(self):
        self._main_loop_task = asyncio.create_task(self._main_loop())

    async def add_task(self, update: Update):
        """
        添加任务：构造任务包装字典，包括重试计数，并放入队列
        :param update: Telegram Update 类型
        """
        message = update.message
        logger.debug(f"Append telegraph task<{message.chat_id}-{message.id}> from {message.from_user.username}")
        task_wrapper = {
            'id': f"{message.chat_id}-{message.id}",
            'retry': 0,
            'srv': None,
            'update': update,
            'task_type': config.BOT_TELEGRAPH_SAVE_FORMAT,
            'return': ""
        }

        async def task_func():
            await TelegraphTask.run(task_wrapper)

        task_wrapper['func'] = task_func
        await self._task_queue.put(task_wrapper)
        # 唤醒 _main_loop 立即处理任务
        self._loop_wakeup.set()

    async def _worker(self, batch_size: int):
        """
        从队列中批量取任务并行运行，若任务出错，在未超过重试次数时重新放回队列
        """
        task_wrappers = []
        for _ in range(batch_size):
            try:
                wrapper = self._task_queue.get_nowait()
                task_wrappers.append(wrapper)
            except asyncio.QueueEmpty:
                break

        if task_wrappers:
            tasks = [wrapper['func']() for wrapper in task_wrappers]
            results = await asyncio.gather(*tasks, return_exceptions = True)

            for wrapper, result in zip(task_wrappers, results):
                update: Update = wrapper['update']
                if isinstance(result, Exception):
                    if wrapper['retry'] < config.TELEGRAPH_HANDLER_RETRY_COUNT:
                        wrapper['retry'] += 1
                        logger.warning(f"Task<{wrapper['id']}> encountered an error: {result} "
                                       f"[Retrying {wrapper['retry']}/{config.TELEGRAPH_HANDLER_RETRY_COUNT}]")
                        await self._task_queue.put(wrapper)
                    else:
                        logger.error(f"Task<{wrapper['id']}> error: {result}")
                        await update.message.reply_markdown(Dialog.KOMGA_TASK_FAILED(result), do_quote = True)
                else:
                    if config.IS_DEBUG_MODE:
                        await update.message.reply_markdown(wrapper['return'], do_quote = True)
                    logger.debug(wrapper['return'])

            for _ in task_wrappers:
                self._task_queue.task_done()

    async def _main_loop(self):
        while True:
            if not self._task_queue.empty():
                self._idle_counter = 0
                q_size = self._task_queue.qsize()
                batch_size = 1 if (q_size == 1 or config.TELEGRAPH_HANDLER_BATCH_SIZE == 1) \
                    else min(q_size, config.TELEGRAPH_HANDLER_BATCH_SIZE)
                await self._worker(batch_size)
            else:
                self._idle_counter += 1

                if self._idle_counter >= config.TELEGRAPH_HANDLER_IDLE_THRESHOLD:
                    sleep_interval = config.TELEGRAPH_HANDLER_IDLE_SLEEP_INTERVAL
                    logger.debug(f"Queue idle, sleeping longer time: {sleep_interval}s")
                else:
                    sleep_interval = 1

                try:
                    await asyncio.wait_for(self._loop_wakeup.wait(), timeout = sleep_interval)
                    self._loop_wakeup.clear()
                except asyncio.TimeoutError:
                    continue
