import dataclasses
import time
from datetime import datetime
from typing import Any, Dict
from uuid import UUID


@dataclasses.dataclass
class PredictionRequest:
    id: UUID
    features: Dict[str, Any]
    start: time.time
    end: time.time

    def todict(self):
        return dataclasses.asdict(self)
