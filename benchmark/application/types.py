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
    complexity_factor: int
    memory_overhead: int
    requests_number: Optional[int] = 10
    runtime: Optional[int] = None
    batch_size: int = 10
    interval: int = 0
    batch_progress: bool = False
    total_progress: bool = False

    def todict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class BenchmarkResult:
    response_list: [PredictionRequest]
    params: BenchmarkParams
    elapsed_time: float

    def todict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
