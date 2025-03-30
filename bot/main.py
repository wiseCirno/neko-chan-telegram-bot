import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot import (
    introduce,
    instructions,
    ChatAnywhereHandler,
    GPT_OK,
    GPT_INIT,
    KOMGA,
    PandoraBox,
    LongSticker,
    TelegraphMessageHandler
)
from src.logger import logger
import src.config as config
from src.service import ProxyService


def main() -> None:
    _proxy = ProxyService.new_proxy(config.PROXY) if config.PROXY else None
    _cmd = config.BOT_COMMAND
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # exit if no bot token
    if not config.BOT_TOKEN:
        logger.error("[Main]: Bot token not set, please fill right params and try again.")
        exit(1)

    # create bot with envs
    neko_chan = (
        ApplicationBuilder().token(config.BOT_TOKEN)
        .proxy(_proxy).get_updates_proxy(_proxy)
        .pool_timeout(30.).connect_timeout(30.).build()
    ) if config.PROXY else (
        ApplicationBuilder().token(config.BOT_TOKEN)
        .pool_timeout(30.).connect_timeout(30.).build()
    )

    # core function: Send Long Sticker
    long = LongSticker(_proxy)
    # core function: Parse contents based on reply
    pandora = PandoraBox(_proxy)

    neko_chan.add_handler(CommandHandler(_cmd['👀'], introduce))
    neko_chan.add_handler(CommandHandler(_cmd['❔'], instructions))
    neko_chan.add_handler(CommandHandler(_cmd['🐉'], long.wan_xx_wan_de, filters.PHOTO | filters.REPLY))
    neko_chan.add_handler(CommandHandler(_cmd['❤️'], pandora.parse, filters.REPLY))
    neko_chan.add_handler(CommandHandler(_cmd['📺'], pandora.anime_search, filters.REPLY))

    if config.MY_USER_ID == -1:
        logger.info("[Main]: User ID not set, telegraph syncing service_old will not work.")
    else:
        # core function: Sync Telegraph manga
        telegraph = TelegraphMessageHandler(config.MY_USER_ID)
        telegraph_monitor = ConversationHandler(
            entry_points = [CommandHandler(_cmd['📖'], telegraph.start)],
            states = {KOMGA: [MessageHandler(filters.TEXT, telegraph.add)]},
            fallbacks = [],
            conversation_timeout = 300
        )
        neko_chan.add_handler(telegraph_monitor)

    # core function: ChatAnywhere GPT conversation
    chat_anywhere = ChatAnywhereHandler(config.MY_USER_ID, config.CHAT_ANYWHERE_KEY,
                                        config.CHAT_ANYWHERE_MODEL, config.CHAT_ANYWHERE_PROMPT, _proxy)
    lets_chat = ConversationHandler(
        entry_points = [CommandHandler(_cmd['💬'], chat_anywhere.new)],
        states = {
            GPT_INIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat_anywhere.get_key)],
            GPT_OK: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat_anywhere.chat)]
        },
        fallbacks = [CommandHandler(_cmd['👋'], chat_anywhere.bye)],
        conversation_timeout = 300
    )
    neko_chan.add_handler(lets_chat)

    try:
        logger.info("[Main]: Initialise Neko Chan......")
        neko_chan.run_polling(allowed_updates = Update.ALL_TYPES)
    except Exception as exc:
        logger.error(f"[Main]: Fatal error in initialization: {exc}")
        exit(1)


if __name__ == "__main__":
    main()
