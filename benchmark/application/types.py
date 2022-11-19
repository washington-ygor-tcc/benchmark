from __future__ import annotations

from enum import Enum, unique
from dataclasses import dataclass, asdict
from typing import (
    Any,
    Dict,
    Optional,
    List,
    Literal,
    overload,
)

from benchmark.core.domain import PredictionRequest
from benchmark.core.types import APIConfig, MessagingConfig

Time = float


@unique
class BenchmarkTypes(str, Enum):
    API = "API"
    MSG = "MSG"


BenchmarkTypesLiteral = Literal[BenchmarkTypes.API, BenchmarkTypes.MSG]


@dataclass
class Config:
    API: APIConfig
    MSG: MessagingConfig

    @overload
    def get(self, benchmark_type: Literal[BenchmarkTypes.API]) -> APIConfig:
        ...

    @overload
    def get(
        self, benchmark_type: Literal[BenchmarkTypes.MSG]
    ) -> MessagingConfig:
        ...

    def get(
        self, benchmark_type: BenchmarkTypesLiteral
    ) -> APIConfig | MessagingConfig:
        match benchmark_type:
            case BenchmarkTypes.API:
                return self.API
            case BenchmarkTypes.MSG:
                return self.MSG
            case _:
                raise NotImplementedError


@dataclass
class BenchmarkParams:
    benchmark_type: BenchmarkTypesLiteral
    complexity_factor: int
    memory_overhead: int
    requests_number: Optional[int] = 10
    runtime: Optional[int] = None
    batch_size: int = 10
    interval: Time = 0
    batch_progress: bool = False
    total_progress: bool = False

    def todict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkResult:
    response_list: List[PredictionRequest]
    params: BenchmarkParams
    elapsed_time: Time

    def todict(self) -> Dict[str, Any]:
        return asdict(self)
