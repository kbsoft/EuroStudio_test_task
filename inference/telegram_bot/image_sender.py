import os
import json
import time
import logging
from threading import Thread

from telegram import Update, ForceReply, File
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from rmq_manager import RMQManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def new_rmq_connection():
    return RMQManager(cfg["user"], cfg["password"], cfg["host"], cfg["port"])


def send(fpath):
    qname = "photo"
    rmq = new_rmq_connection()
    rmq.queue_declare(qname)
    message = json.dumps({"path": fpath})
    rmq.send(qname, message)


def write_to_file(data):
    f = open("result.txt", "w")
    f.write(data)
    f.close()


def update_result(ch, method, properties, body):
    logging.info(f"New body: {body}")
    write_to_file(body.decode())


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    msg = (
        fr"Здравствуйте, {user.mention_markdown_v2()}\!"
        "\nЗагрузите изображение и дождитесь результатов распознавания"
    )
    update.message.reply_markdown_v2(msg)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Загрузите изображение и дождитесь ответа")


def save_and_send(image):
    fpath = os.path.join(ROOT_DIR, image.file_unique_id)
    tg_file = image.get_file()
    tg_file.download(custom_path=fpath)
    send(fpath)
    file_empty = True
    while file_empty:
        with open("result.txt", "r", encoding="utf-8") as f:
            data = f.read()
            if data:
                file_empty = False
                result = json.loads(data)
            time.sleep(0.1)
    logging.info(f"Result: {result}")
    write_to_file("")
    return (
        "Id: " + str(result["class_id"]) +
        "\nНазвание: " + str(result["name"]) +
        "\nУверенность: " + str(result["confidence"])
    )


def send_image_to_ml(update: Update, context: CallbackContext) -> None:
    """Send image to ML if photo uploaded."""
    logging.info(update)
    msg = "Не удалось обработать изображение"
    try:
        image = update.message.document
        if image and image.mime_type.startswith("image/"): 
            msg = save_and_send(image)
        elif update.message.photo:
            try:
                msg = save_and_send(update.message.photo[2])
            except IndexError:
                msg = save_and_send(update.message.photo[1])
        update.message.reply_text(msg)
    except Exception as e:
        update.message.reply_text(msg)
        logging.error(f"Exception: {e}")
        pass


def main() -> None:
    """Start the bot."""
    
    updater = Updater(cfg["token"])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.all, send_image_to_ml))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    with open("cfg.json") as f:
        cfg = json.loads(f.read())

    ROOT_DIR = cfg["root_dir"]

    qname = "ml_result"
    listener = new_rmq_connection()
    listener.queue_declare(qname)
    t = Thread(
        target=listener.listen,
        args=(
            qname,
            update_result,
        ),
    )
    t.start()

    main()

