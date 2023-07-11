import json
import os


class Settings(dict):
    def __init__(self, mapping: dict):
        mapping = { 
            key.upper(): Settings(value) if isinstance(value, dict) else value 
            for key, value in mapping.items() 
        }
        super().__init__(mapping)

    def __getattr__(self, name):
        return self.__getitem__(name.upper())

    def __setattr__(self, name, value):
        self.__setitem__(name,value)
        
    def __getitem__(self, name):
        return super().__getitem__(name.upper())

    def __setitem__(self, name, value):
        name = name.upper()
        value = Settings(value) if isinstance(value, dict) else value 
        super().__setitem__(name, value)


settings = Settings({
    "PROJECT_DB_API_KEY": os.getenv("PROJECT_DB_API_KEY", ""),
    "DB_HOST": os.getenv("DB_HOST", "localhost:8080"),
    "IMPORT_INTERVAL": int(os.getenv('IMPORT_INTERVAL', 86400)), # 24h
    "BATCH_INTERVAL": int(os.getenv('BATCH_INTERVAL', 300)), # 5 min
    "BATCH_SIZE": int(os.getenv("BATCH_SIZE", 100)),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "ERROR"),
    "MQ_HOST": os.getenv("MQ_HOST", "mq"),
    "MQ_EXCHANGE": os.getenv("MQ_EXCHANGE", "zhaw-km"),
    "MQ_HEARTBEAT": int(os.getenv("MQ_HEARTBEAT", 6000)),
    "MQ_TIMEOUT": int(os.getenv("MQ_TIMEOUT", 3600))
})

for path in ["/etc/app/config.json", "/etc/app/secrets.json"]:
    if os.path.exists(path):
        with open(path) as file:
            values = json.load(file)
            settings.update(values)
