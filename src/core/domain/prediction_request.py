import dataclasses
import time

from src.core.types import Features, Id
from typing import Dict, Any


@dataclasses.dataclass
class PredictionRequest:
    id: Id
    features: Features
    start: time.time
    end: time.time

    def todict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
