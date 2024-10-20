import logging
import json
from datetime import datetime

class RedisMessage:
    def __init__(self, type: str, entity: str):
        now = datetime.now()
        self.type = type
        self.entity = entity
        self.time = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.payload = {
            'property': "",
            'value': "",
            'message': "",
        }

    def from_log(self, message: logging.LogRecord):
        self.payload = {
            'property': message.levelname,
            'value': message.lineno,
            'message': message.message,
        }

    def data(self,property: str, value: str, message: str ):
        self.payload = {
            'property': property,
            'value': value,
            'message': message,
        }



    def json(self):
        _json = {
            'type' : self.type,
            'entity': self.entity,
            'time': self.time,
            'payload': self.payload,
        }
        return json.dumps(_json)