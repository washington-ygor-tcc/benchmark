import dataclasses
import time

from benchmark.core.types import Features, Id
from typing import Dict, Any


@dataclasses.dataclass
class PredictionRequest:
    request_id: Id
    features: Features
    start: time.time = None
    end: time.time = None

    def todict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
