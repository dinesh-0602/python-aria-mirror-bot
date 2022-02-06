import threading

from telegram.ext import CommandHandler, run_async

from bot import LOGGER, dispatcher
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import auto_delete_message, sendMessage

@run_async
def list_drive(update, context):
    message = update.message.text
    search = message.split(' ',maxsplit=1)[1]
    LOGGER.info(f"Searching: {search}")
    gdrive = GoogleDriveHelper(None)
    if msg := gdrive.drive_list(search):
        reply_message = sendMessage(msg, context.bot, update)
    else:
        reply_message = sendMessage('No result found', context.bot, update)

    threading.Thread(target=auto_delete_message, args=(context.bot, update.message, reply_message)).start()


list_handler = CommandHandler(BotCommands.ListCommand, list_drive,filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
dispatcher.add_handler(list_handler)
