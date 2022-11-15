import enum

from dataclasses import dataclass
from typing import Any, Dict, TypedDict, Optional

from benchmark.core.domain.prediction_request import PredictionRequest


class APIConfig(TypedDict):
    host: str
    port: int
    prediction_route: str


class MessagingConfig(TypedDict):
    host: str
    port: int
    request_channel: str
    response_channel: str


class Config(TypedDict):
    API: APIConfig
    MSG: MessagingConfig


@enum.unique
class BenchmarkTypes(str, enum.Enum):
    API = "API"
    MSG = "MSG"


@dataclass
class BenchmarkParams:
    benchmark_type: BenchmarkTypes
    requests_number: int
    batch_size: int
    complexity_factor: int
    memory_overhead: int
    interval: int
    runtime: Optional[int]
    batch_progress: bool = False
    total_progress: bool = False

    def todict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class BenchmarkResult:
    results: [PredictionRequest]
    params: BenchmarkParams

    def todict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
