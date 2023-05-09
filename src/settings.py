import json
import os

_settings = {
    "DB_HOST": os.getenv("DB_HOST", "db:8080"),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "ERROR"),
    "MQ_HOST": "mq",
    "MQ_EXCHANGE": "zhaw-km",
    "MQ_BINDKEYS": ["importer.projects"],
    "MQ_HEARTBEAT": 6000,
    "MQ_TIMEOUT": 3600,
    "MQ_QUEUE": "indexqueue",
    "GH_SECRET": os.getenv("GH_SECRET", ""),
}

if os.path.exists("/etc/app/secrets.json"):
    with open("/etc/app/secrets.json") as secrets_file:
        config = json.load(secrets_file)
        for key in config.keys():
            if config[key] is not None:
                _settings[str.upper(key)] = config[key]


DB_HOST = _settings["DB_HOST"]
LOG_LEVEL = _settings["LOG_LEVEL"]
MQ_HOST = _settings["MQ_HOST"]
MQ_EXCHANGE = _settings["MQ_EXCHANGE"]
MQ_BINDKEYS = _settings["MQ_BINDKEYS"]
MQ_HEARTBEAT = _settings["MQ_HEARTBEAT"]
MQ_TIMEOUT = _settings["MQ_TIMEOUT"]
MQ_QUEUE = _settings["MQ_QUEUE"]
GH_SECRET = _settings["GH_SECRET"]
