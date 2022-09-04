import dataclasses
import time

from benchmark.core.types import Features, Id, Prediction
from typing import Dict, Any


@dataclasses.dataclass
class PredictionRequest:
    request_id: Id
    features: Features
    start: time.time = None
    end: time.time = None
    prediction: Prediction = None

    def todict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
