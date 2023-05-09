class Importer:
    def __init__(self, database, message_queue):
        self._database = database
        self._message_queue = message_queue

    
    def run(self):
        print('Running import')