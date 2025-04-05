import asyncio
import json
from typing import Optional

from telegram import Update
from telegram.ext import ConversationHandler

import src.config as config
from bot.state import KOMGA_HANDLER_ACTIVATED
from src.dialog import KomgaDialog
from src.logger import logger
from src.model import Telegraph
from src.service import TelegraphService
from src.task import TelegraphTask


class TelegraphHandler:
    def __init__(self):
        self._batch_size = 0
        self._task_queue = asyncio.Queue()
        self._idle_counter = 0
        self._loop_wakeup = asyncio.Event()
        self._main_loop_task = None

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
                        await update.message.reply_markdown(KomgaDialog.TASK_FAILED(result), do_quote = True)
                else:
                    if config.IS_DEBUG_MODE:
                        await update.message.reply_markdown(wrapper['return'], do_quote = True)
                    logger.debug(wrapper['return'])

            for _ in task_wrappers:
                self._task_queue.task_done()
                self._batch_size -= 1

    async def _main_loop(self):
        while True:
            if not self._task_queue.empty():
                self._idle_counter = 0
                q_size = self._task_queue.qsize()
                self._batch_size = 1 if (q_size == 1 or config.TELEGRAPH_HANDLER_BATCH_SIZE == 1) \
                    else min(q_size, config.TELEGRAPH_HANDLER_BATCH_SIZE)
                await self._worker(self._batch_size)
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

    async def start_loop(self):
        self._main_loop_task = asyncio.create_task(self._main_loop())

    async def add_task(self, update: Update, download: bool = False):
        """
        添加任务：构造任务包装字典，包括重试计数，并放入队列
        :param update: Telegram Update 类型
        :param download: 选择是否要下载到本地，默认是否
        """
        message = update.message
        logger.debug(f"Append telegraph task<{message.chat_id}-{message.id}> from {message.from_user.username}")
        task_wrapper = {
            'id': f"{message.chat_id}-{message.id}",
            'retry': 0,
            'srv': None,
            'update': update,
            'task_type': config.TELEGRAPH_SAVE_EXTENSION if download else "no_file",
            'return': ""
        }

        async def task_func():
            await TelegraphTask.run(task_wrapper)

        task_wrapper['func'] = task_func
        await self._task_queue.put(task_wrapper)
        # 唤醒 _main_loop 立即处理任务
        self._loop_wakeup.set()

    @staticmethod
    async def _random_from_database() -> Optional[Telegraph]:
        return await TelegraphService.query_from_database()

    @staticmethod
    async def _search_from_database(raw: str) -> Optional[Telegraph]:
        try:
            query_dict = json.loads(raw)
            return await TelegraphService.query_from_database(query_dict['title'], query_dict)
        except json.decoder.JSONDecodeError:
            return None

    @staticmethod
    def _get_update_param(update: Update) -> (str, str):
        split_text = update.message.text.split(maxsplit = 2)
        if len(split_text) > 1:
            return split_text[1].strip(), split_text[2].strip() if len(split_text) == 3 else ""
        return "", ""

    async def _process_command(self, update: Update, parameter: (str, str), fallback: bool = False) -> int:
        param1, param2 = parameter
        return_state = KOMGA_HANDLER_ACTIVATED if fallback else ConversationHandler.END

        if param1 == "":
            await update.message.reply_markdown(KomgaDialog.EMPTY)
            return return_state

        if param1 == "help":
            await update.message.reply_text(KomgaDialog.HELP)
            return return_state

        if param1 == "status":
            await update.message.reply_text(KomgaDialog.STATUS(self._task_queue.qsize(), self._batch_size))
            return return_state

        if param1 == "random":
            telegraph_obj = await self._random_from_database()
            await update.message.reply_html(KomgaDialog.RANDOM(telegraph_obj), do_quote = False)
            return return_state

        if param1 == "search":
            if not param2:
                await update.message.reply_markdown(KomgaDialog.SEARCH_FALLBACK)
                return return_state
            try:
                result = await self._search_from_database(param2)
                await update.message.reply_html(KomgaDialog.SEARCH(result))
            except IndexError:
                await update.message.reply_markdown(KomgaDialog.SEARCH_FALLBACK)
            return return_state

        if param1 == "stop":
            if fallback:
                await update.message.reply_text(KomgaDialog.STOP(self._batch_size == 0))
                return ConversationHandler.END

            await update.message.reply_text(KomgaDialog.NOT_STARTED)
            return ConversationHandler.END

        if param1 == "start":
            if fallback:
                await update.message.reply_text(KomgaDialog.ALREADY_STARTED)
                return KOMGA_HANDLER_ACTIVATED

            if update.message.from_user.id != config.MY_USER_ID:
                await update.message.reply_text(KomgaDialog.USER_UNAUTHORIZED(update.message))
                return ConversationHandler.END

            await update.message.reply_text(KomgaDialog.USER_AUTHORIZED(update.message))
            return KOMGA_HANDLER_ACTIVATED

        await update.message.reply_text(KomgaDialog.UNSUPPORTED(param1))

        return KOMGA_HANDLER_ACTIVATED if fallback else ConversationHandler.END

    async def handle_start(self, update: Update) -> int:
        return await self._process_command(update, self._get_update_param(update))

    async def handle_fallback(self, update: Update) -> int:
        return await self._process_command(update, self._get_update_param(update), fallback = True)
