from __future__ import annotations
import dataclasses

from benchmark.core.types import Features, Id, Prediction
from typing import Dict, Any

__all__ = ["PredictionRequest"]


@dataclasses.dataclass
class PredictionRequest:
    request_id: Id
    features: Features
    start: float = None
    end: float = None
    prediction: Prediction = None

    def todict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
