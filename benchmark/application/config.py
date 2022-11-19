import os
import yaml
import pkg_resources

from enum import Enum
from typing import Union, Dict
from benchmark.application.types import (
    Config,
    APIConfig,
    MessagingConfig,
    BenchmarkTypes,
)


class Env(str, Enum):
    LOCAL = "local"
    DOCKER = "docker"


def get_default_config(
    path: Union[str, os.PathLike] = "../config.yaml",
    enviroment: Env = Env.LOCAL,
):

    config = dict(
        yaml.safe_load(pkg_resources.resource_string(__name__, str(path)))
    )
    env_config: Dict = config[enviroment]

    return Config(
        API=APIConfig.fromdict(env_config[BenchmarkTypes.API]),
        MSG=MessagingConfig.fromdict(env_config[BenchmarkTypes.MSG]),
    )
