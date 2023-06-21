import time
import pika
import settings
import hookup
from logger import logger


if __name__ == "__main__":
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=settings.MQ_HOST,
                                heartbeat=settings.MQ_HEARTBEAT,
                                blocked_connection_timeout=settings.MQ_TIMEOUT))
    channel = connection.channel()
    channel.exchange_declare(exchange=settings.MQ_EXCHANGE, exchange_type="topic")

    while True:
        logger.info("start import")
        try:
            hookup.run(channel)
        except:
            logger.exception('Unhandled exception')
        logger.info("finished import") 
        time.sleep(settings.IMPORT_INTERVAL)
