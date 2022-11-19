import inspect
from typing import Callable, Dict, Any, Generator, List
from dataclasses import dataclass


Total = int
Current = int
Id = int | str
Features = Dict[str, Any]
Prediction = Dict[str, Any]
RequestGenerator = Generator[List[Features], None, None]
ProgressIndicator = Callable[[Current, Total], None]


@dataclass
class Config:
    @classmethod
    def fromdict(cls, config: Dict | None = None, **kwargs):
        if config is None:
            config = {}
        return cls(
            **{
                k: v
                for k, v in dict(config, **kwargs).items()
                if k in inspect.signature(cls).parameters
            }
        )


@dataclass
class APIConfig(Config):
    host: str
    port: int
    prediction_route: str


@dataclass
class MessagingConfig(Config):
    host: str
    port: int
    request_channel: str
    response_channel: str
