import datetime
import json
import uuid
import asyncio

from typing import Dict
from benchmark.core.types import Id
from dataclasses import dataclass, field


def json_default_serializer(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return obj.hex
    return json.JSONEncoder.default(obj)


@dataclass
class FutureResponses:
    responses: Dict[Id, asyncio.Future] = field(default_factory=dict)

    def set(self, response_id: Id):
        self.responses.update({response_id: self.loop.create_future()})

    def remove(self, response_id: Id):
        self.responses.pop(response_id, None)

    def get(self, response_id: Id):
        return self.responses.get(response_id)

    def has(self, response_id: Id):
        return response_id in self.responses

    def set_result(self, response_id: Id, result):
        if self.has(response_id) and not self.get(response_id).done():
            self.get(response_id).set_result(result)

    def is_empty(self) -> bool:
        return len(self.responses) == 0

    @property
    def loop(self):
        return asyncio.get_event_loop()
