import json
import os

_settings = {
    "PROJECT_DB_API_KEY": os.getenv("PROJECT_DB_API_KEY", ""),
    "DB_HOST": os.getenv("DB_HOST", "localhost:8080"),
    "IMPORT_INTERVAL": int(os.getenv('IMPORT_INTERVAL', 86400)), # 24h
    "BATCH_INTERVAL": int(os.getenv('BATCH_INTERVAL', 300)), # 5 min
    "BATCH_SIZE": int(os.getenv("BATCH_SIZE", 100)),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "ERROR"),
    "MQ_HOST": "mq",
    "MQ_EXCHANGE": "zhaw-km",
    "MQ_HEARTBEAT": 6000,
    "MQ_TIMEOUT": 3600
}

if os.path.exists("/etc/app/secrets.json"):
    with open("/etc/app/secrets.json") as secrets_file:
        config = json.load(secrets_file)
        for key in config.keys():
            if config[key] is not None:
                _settings[str.upper(key)] = config[key]

PROJECT_DB_API_KEY = _settings["PROJECT_DB_API_KEY"]
DB_HOST = _settings["DB_HOST"]
IMPORT_INTERVAL = _settings['IMPORT_INTERVAL']
BATCH_INTERVAL = _settings['BATCH_INTERVAL']
BATCH_SIZE = _settings['BATCH_SIZE']
LOG_LEVEL = _settings["LOG_LEVEL"]
MQ_HOST = _settings["MQ_HOST"]
MQ_EXCHANGE = _settings["MQ_EXCHANGE"]
MQ_HEARTBEAT = _settings["MQ_HEARTBEAT"]
MQ_TIMEOUT = _settings["MQ_TIMEOUT"]
