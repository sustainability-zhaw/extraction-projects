import logging
import pika
from flask import Flask
import waitress

import settings
from database import Database
from importer import Importer
from webhook import Webhook


logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)
logger = logging.getLogger("extractor-projects")

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=settings.MQ_HOST,
    heartbeat=settings.MQ_HEARTBEAT,
    blocked_connection_timeout=settings.MQ_TIMEOUT
))
channel = connection.channel()
channel.exchange_declare(exchange=settings.MQ_EXCHANGE, exchange_type="topic")
result = channel.queue_declare(settings.MQ_QUEUE, exclusive=False)

database = Database(settings.DB_HOST)
importer = Importer(database, channel)

app = Flask(__name__)
webhook = Webhook(app)


@webhook.route('/webhook', settings.GH_SECRET)
def handle_webhook(data):
    # TODO: Check if excel file changed
    print(data)
    importer.run() # Start async (Will cancel and restart if already running)


importer.run() # Start async
waitress.serve(app, port=8080)
