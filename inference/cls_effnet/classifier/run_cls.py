import os
import json
import struct
import logging
import queue
import multiprocessing
from contextlib import suppress
from time import sleep

import cv2
import numpy as np
import torch
import hydra
from rmq_manager import RMQManager
from efficientnet_pytorch import EfficientNet
import albumentations as A
from albumentations.pytorch import ToTensorV2

from omegaconf import DictConfig
from rmq import rmq_step_listen

logging.basicConfig(
    format="[%(asctime)s %(levelname)s] %(message)s",
    level=logging.DEBUG,
)


def test_transform(img_size=240):
    transform = A.Compose(
        [
            A.LongestMaxSize(max_size=img_size, always_apply=True, interpolation=3),
            A.PadIfNeeded(min_height=img_size, min_width=img_size),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2(),
        ]
    )

    return transform


@torch.no_grad()
def prediction_worker(
    predict_queue: multiprocessing.Queue,
    img_path_queue: multiprocessing.Queue,
    stop: multiprocessing.Event,
    ml_init_done: multiprocessing.Event,
    cfg: DictConfig,
):
    transform = test_transform()
    model = EfficientNet.from_pretrained(
        "efficientnet-b1",
        num_classes=cfg.CLS.NUM_CLASSES,
    ).to(cfg.CLS.DEVICE)

    logging.info("Efficientnet model loaded")
    model.load_state_dict(
        torch.load(cfg.CLS.CHECKPOINT_PATH, map_location=torch.device(cfg.CLS.DEVICE))
    )
    model.eval()
    logging.info("Efficientnet checkpoint loaded")
    ml_init_done.set()

    while not stop.is_set():
        # Remain step unchainged if there is no new  messages
        try:
            img_path = img_path_queue.get_nowait()

            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            image_tranformed = transform(image=img)["image"].to(cfg.CLS.DEVICE)
            output = model(torch.unsqueeze(image_tranformed, 0))
            _, preds = torch.max(output, 1)
            pred = int(preds.data.cpu().numpy()[0])
            conf = torch.nn.functional.softmax(output).data.cpu().numpy().max()

            with suppress(queue.Full):
                predict_queue.put_nowait({"class_id": pred, "conf": conf})
        except queue.Empty:
            sleep(1 / 2)
            continue

    predict_queue.cancel_join_thread()


@hydra.main(config_path="/workspace/configs", config_name="config")
def run_cls(cfg: DictConfig):

    # Init queues and multiprocessing events
    predict_queue = multiprocessing.Queue(1)
    img_path_queue = multiprocessing.Queue(1)
    ml_init_done = multiprocessing.Event()
    stop = multiprocessing.Event()

    # Start detection process
    cls_process = multiprocessing.Process(
        target=prediction_worker,
        args=(predict_queue, img_path_queue, stop, ml_init_done, cfg),
    )

    cls_process.start()
    ml_init_done.wait()

    # Connect ot RMQ server
    logging.info(f"Connecting to RMQ at host {cfg.RMQ.HOST} as '{cfg.RMQ.USER}'...")
    rmq = RMQManager(user=cfg.RMQ.USER, password=cfg.RMQ.PASSWORD, host=cfg.RMQ.HOST)
    logging.info("Connected to RMQ.")
    rmq.queue_declare(cfg.RMQ.QUEUE.ML)
    logging.info("Connected to RMQ")

    # Start RMQ step listener process
    rmq_step_listen(img_path_queue, cfg)

    while True:
        try:
            pred = predict_queue.get_nowait()
            logging.info("Get new pred: {pred}")
        except queue.Empty:
            sleep(0.1)
            logging.info("Empty")
            continue

        logging.debug(f"Sending new predict to RMQ...")
        logging.info(f"Predicted class - {pred}")

        class_id = int(pred["class_id"])
        conf = round(float(pred["conf"]), 5)
        rmq.send(
            routing_key=cfg.RMQ.QUEUE.ML,
            message=json.dumps(
                {
                    "class_id": class_id,
                    "name": str(list(cfg.CLS.CLASS_NAME)[class_id]),
                    "confidence": conf,
                },
                ensure_ascii=False,
            ).encode("utf8"),
        )

    stop.set()
    cls_process.join()


if __name__ == "__main__":
    run_cls()
