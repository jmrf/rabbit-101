import logging
import os
import sys
import time

import coloredlogs
import pika

from .constants import HEARTBEAT
from .constants import QUEUE_NAME


logger = logging.getLogger(__name__)


def do_some_work(hard_work_time: int) -> None:
    print("----")
    logger.info(f"Working hard for {hard_work_time} seconds..")
    time.sleep(hard_work_time)


def callback(ch, method, properties, body):

    do_some_work(body.count(b"."))

    logger.info("🍻 Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", heartbeat=HEARTBEAT)
    )
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print("⌛ Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":

    log_level = logging.DEBUG
    coloredlogs.install(logger=logger, level=log_level)

    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
