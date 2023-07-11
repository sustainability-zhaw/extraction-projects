import logging
import time

import pika

import importer
from settings import settings


logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

logging.getLogger("pika").setLevel(logging.WARNING)

if __name__ == "__main__":
    logger.info(f"init message queue connection to host '{settings.MQ_HOST}'")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.MQ_HOST,
            heartbeat=settings.MQ_HEARTBEAT,
            blocked_connection_timeout=settings.MQ_TIMEOUT
        )
    )

    channel = connection.channel()
    channel.exchange_declare(settings.MQ_EXCHANGE, exchange_type="topic")

    while True:
        try:
            logger.info("Running import")
            importer.run(channel)
        except:
            logger.exception('Unhandled exception')

        logger.info(f"Import completed. Waiting {settings.IMPORT_INTERVAL} seconds before next import run.") 
        time.sleep(settings.IMPORT_INTERVAL)
