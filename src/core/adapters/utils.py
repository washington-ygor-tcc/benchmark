import datetime
import json
import uuid


def json_default_serializer(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return obj.hex
    return json.JSONEncoder.default(obj)