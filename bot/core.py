import asyncio
import re
from io import BytesIO
from typing import Optional

from PIL import Image
from fake_useragent import UserAgent
from httpx import Proxy
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes, filters

import src.config as config
from src.api import ChatAnywhereApi, TraceMoeApi
from src.handler import TelegraphHandler
from src.logger import logger
from src.service_old import AggregationSearch
from state import *


class LongSticker:
    def __init__(self, proxy: Optional[Proxy] = None, cloudflare_worker_proxy: Optional[Proxy] = None):
        self._proxy = proxy
        self._cf_proxy = cloudflare_worker_proxy
        self._headers = {'User-Agent': UserAgent().random}

    async def wan_xx_wan_de(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        async def composition(b: bytes) -> bytes:
            with Image.open("res/sticker/玩XX玩的.jpg") as background, \
                    Image.open(BytesIO(b)) as overlay:

                ratio = overlay.size[0] / overlay.size[1]

                if 0.66 <= ratio <= 1.5:
                    overlay = overlay.resize(
                        (115, int(overlay.size[1] * 115 / overlay.size[0])),
                        resample = Image.Resampling.BICUBIC
                    )
                    background.paste(overlay, (145, 370))

                elif ratio > 1.5:
                    overlay = overlay.resize(
                        (190, int(overlay.size[1] * 190 / overlay.size[0])),
                        resample = Image.Resampling.BICUBIC
                    )
                    background.paste(overlay, (115, 410))

                else:
                    overlay = overlay.resize(
                        (60, int(overlay.size[1] * 60 / overlay.size[0])),
                        resample = Image.Resampling.BICUBIC
                    )
                    background.paste(overlay, (180, 350))

                image_bytes = BytesIO()
                background.save(image_bytes, 'WEBP')
                return image_bytes.getvalue()

        media_task = AggregationSearch(proxy = self._proxy, cf_proxy = self._cf_proxy)
        file_id = None

        message = update.message.reply_to_message or update.message

        if filters.PHOTO.filter(message):
            file_id = message.photo[2].file_id
        elif filters.Sticker.STATIC.filter(message):
            file_id = message.sticker.file_id
        elif filters.Document.IMAGE.filter(message):
            file_id = message.document.file_id

        if file_id:
            media = await media_task.get_media((await context.bot.get_file(file_id)).file_path)
            await update.message.reply_sticker(await composition(media))
        else:
            await update.message.reply_text("Neko看了一眼并朝你抛出了一个异常")

        return ConversationHandler.END


class PandoraBox:
    def __init__(self, proxy: Optional[Proxy] = None, cloudflare_worker_proxy: Optional[str] = None):
        self._proxy = proxy
        self._cf_proxy = cloudflare_worker_proxy
        self._headers = {'User-Agent': UserAgent().random}

    async def parse(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        async def search_and_reply(url):
            results = await AggregationSearch(self._proxy, self._cf_proxy).aggregation_search(url)
            m, b = "🔎 _搜索结果_ ", []

            if not results:
                await update.message.reply_text("没有搜到结果 TwT")
                return ConversationHandler.END

            for i, r in enumerate(results):
                def add_title_button(c: str):
                    if r['title'] and len(r['title']) < 20:
                        b.append([InlineKeyboardButton(r['title'], r['url'])])
                    elif r['title'] and len(r['title']) >= 20:
                        b.append([InlineKeyboardButton(f"{r['title'][:20]}...", r['url'])])
                    else:
                        b.append([InlineKeyboardButton(c, r['url'])])

                m += f" [{i + 1}]({r['url']})"
                if r["class"] == "iqdb":
                    b.append([InlineKeyboardButton(r['source'], r['url'])])
                elif r["class"] == "ascii2d":
                    add_title_button("Ascii2D")
                    if r['author'] and len(r['author']) < 20:
                        b.append([InlineKeyboardButton(r['author'], url = r['author_url'])])
                    elif r['author'] and len(r['author']) >= 20:
                        b.append([InlineKeyboardButton(f"{r['author'][:20]}...", url = r['author_url'])])
                elif r["class"] == "google":
                    add_title_button("Google")

            await update.message.reply_markdown(m, reply_markup = InlineKeyboardMarkup(b))

        # start from here
        link_preview = update.message.reply_to_message.link_preview_options
        attachment = update.message.reply_to_message.effective_attachment

        if link_preview:
            if re.search(r'booru|x|twitter|pixiv|ascii2d|saucenao', link_preview.url):
                await update.message.reply_text("这...这不用来找我吧(")
            else:
                await search_and_reply(link_preview.url)
            return ConversationHandler.END

        reply_message = update.message.reply_to_message

        if filters.PHOTO.filter(reply_message):
            photo_file = reply_message.photo[2]
            file_link = (await context.bot.get_file(photo_file.file_id)).file_path
            await search_and_reply(file_link)

        elif filters.Sticker.STATIC.filter(reply_message) or filters.ANIMATION.filter(reply_message):
            sticker_task = AggregationSearch(proxy = self._proxy, cf_proxy = self._cf_proxy)
            media = await sticker_task.get_media((await context.bot.get_file(attachment.file_id)).file_path)

            if filters.Sticker.STATIC.filter(reply_message):
                await update.message.reply_photo(photo = media)
            else:
                await update.message.reply_document(media, filename = f"{attachment.file_unique_id}.webm")

        elif filters.Document.IMAGE.filter(reply_message):
            file_link = (await context.bot.get_file(reply_message.document.thumbnail.file_id)).file_path
            await search_and_reply(file_link)

        else:
            await update.message.reply_text("Neko看了一眼并朝你抛出了一个异常")

        return ConversationHandler.END

    async def anime_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        async def search_and_reply(url):
            def format_time(seconds):
                return f"{int(seconds) // 60}m {int(seconds) % 60}s"

            result = (await TraceMoeApi(self._proxy, self._cf_proxy).search(url, 'cut_boarder'))[0]

            if result['similarity'] <= 0.8:
                await update.message.reply_text("没有发现搜索结果 XwX")
                return ConversationHandler.END

            anime_url = f"https://anilist.co/anime/{result['anilist']}"
            buttons = [
                [InlineKeyboardButton("AniList 详情页", url = anime_url)],
                [InlineKeyboardButton("图片预览", url = result['image'])],
                [InlineKeyboardButton("视频切片预览", url = result['video'])],
            ]

            reply = (
                f"[🔎]({anime_url}) _搜索结果_\n\n"
                f"空降第 {result['episode']} 集 "
                f"{format_time(float(result['from']))} - {format_time(float(result['to']))}"
            )

            await update.message.reply_markdown(reply, reply_markup = InlineKeyboardMarkup(buttons))

        # Start from here
        link_preview = update.message.reply_to_message.link_preview_options

        if link_preview:
            await search_and_reply(link_preview.url)

        if filters.PHOTO.filter(update.message.reply_to_message):
            photo = update.message.reply_to_message.photo[2]
            await search_and_reply((await context.bot.get_file(photo.file_id)).file_path)
            return ConversationHandler.END

        if filters.Document.IMAGE.filter(update.message.reply_to_message):
            attachment = update.message.reply_to_message.effective_attachment
            await search_and_reply((await context.bot.get_file(attachment.thumbnail.file_id)).file_path)
            return ConversationHandler.END

        await update.message.reply_text("Neko看了一眼并朝你抛出了一个异常")
        return ConversationHandler.END


class TelegraphMessageHandler:
    def __init__(self):
        self._handler: TelegraphHandler = TelegraphHandler()
        asyncio.get_event_loop().create_task(self._handler.start_loop()) if config.MY_USER_ID != -1 else None

    async def start(self, update: Update, _):
        return await self._handler.handle_start(update)

    async def fallback(self, update: Update, _):
        return await self._handler.handle_fallback(update)

    async def add(self, update: Update, _):
        await self._handler.add_task(update, True)


class ChatAnywhereHandler:
    def __init__(
            self,
            user_id: int = -1,
            key: str | None = None,
            model: str = "gpt-3.5-turbo",
            prompt: str = "You are a helpful assistant.",
            proxy: Optional[Proxy] = None,
            cloudflare_worker_proxy: Optional[str] = None,
    ):
        self._key = key
        self._model = model
        self._prompt = prompt
        self._user_id = user_id
        self._proxy = proxy
        self._cf_proxy = cloudflare_worker_proxy
        self._hosted_instances = {}

    async def _add_instance(self, chat_id: int, instance: ChatAnywhereApi):
        self._hosted_instances[chat_id] = instance

    async def new(self, update: Update, _):
        if update.message.chat.type in ['group', 'supergroup', 'channel']:
            await update.message.reply_text(text = "Neko 并不能在群组或频道内打开这个功能 XwX")
            return ConversationHandler.END

        if not self._key:
            await update.message.reply_text(text = "未配置 Chat Anywhere 密钥🔑")
            await update.message.reply_text("在这里发送密钥给 Neko 来启用聊天功能，发送后消息会被自动删除 c:")
            return GPT_INIT

        if update.message.from_user.id == self._user_id:
            await self._add_instance(
                update.message.from_user.id,
                ChatAnywhereApi(token = self._key, proxy = self._proxy)
            )
            await update.message.reply_text("准备OK c:")
            return GPT_OK

    async def get_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        user_id = update.message.from_user.id

        await context.bot.delete_message(chat_id, message_id)
        await self._add_instance(user_id, ChatAnywhereApi(token = update.message.text, proxy = self._proxy))

        try:
            await self._hosted_instances[user_id].list_model()
            await update.message.reply_text(text = "准备OK c:")
            return GPT_OK
        except Exception as exc:
            logger.error(f'[Chat Mode]: {exc}')
            self._hosted_instances.pop(user_id)
            await update.message.reply_text(text = "唔...无效的密钥，再用 /chat 试试吧")
            return ConversationHandler.END

    async def chat(self, update: Update, _):
        user_input = update.message.text_markdown
        user_id = update.message.from_user.id

        try:
            result = await self._hosted_instances[user_id].chat(user_input, self._prompt, self._model)
            message = result['answers'][0]['message']['content']
            await update.message.reply_text(text = message)
        except Exception as exc:
            logger.error(f'[Chat Mode]: {exc}')
            await update.message.reply_text(str(exc))

    async def bye(self, update: Update, _):
        self._hosted_instances.pop(update.message.from_user.id)
        await update.message.reply_text("拜拜啦～")
        return ConversationHandler.END
