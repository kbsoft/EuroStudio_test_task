import os
import json
import logging
import queue
import multiprocessing
from contextlib import suppress
from omegaconf import DictConfig
from rmq_manager import RMQManager
from threading import Thread


logging.basicConfig(
    format="[%(asctime)s %(levelname)s] %(message)s",
    level=logging.DEBUG,
)


def rmq_step_listen(
    out_queue: multiprocessing.Queue,
    cfg: DictConfig,
):
    """
    Слушатель сообщений от Controller
    """

    rmq = RMQManager(user=cfg.RMQ.USER, password=cfg.RMQ.PASSWORD, host=cfg.RMQ.HOST)
    rmq.queue_declare(cfg.RMQ.QUEUE.PHOTO)

    logging.info(f"RMQ Start listen {cfg.RMQ.QUEUE.PHOTO}")

    def msg_handler(ch, method, properties, body):
        # if method.exchange != exchange_name:
        #     return
        if not body:
            logging.debug(f"response from {method.exchange} is equal")
            return
        current_step = json.loads(body)
        logging.debug(f"Body: {body}")
        if not current_step or "path" not in current_step:
            logging.debug("path 'step' not found")
            return

        with suppress(queue.Full):
            logging.debug(f"Get new step: {current_step['path']}")
            out_queue.put_nowait((current_step["path"]))

    listener_thread = Thread(
        target=rmq.listen, args=(cfg.RMQ.QUEUE.PHOTO, msg_handler), daemon=True
    )

    listener_thread.start()
    out_queue.cancel_join_thread()
