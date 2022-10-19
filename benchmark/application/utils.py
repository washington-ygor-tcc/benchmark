import os
import pkg_resources
import yaml
import collections.abc


from datetime import datetime
from typing import Dict, Union


def update_config(update: Dict, config: Dict) -> Dict:
    for key, value in update.items():
        if isinstance(value, collections.abc.Mapping):
            config[key] = update_config(value, config.get(key, {}))
        else:
            config[key] = value
    return config


def get_default_config(path: Union[str, os.PathLike] = "../config.yaml"):
    return yaml.safe_load(pkg_resources.resource_string(__name__, path))


def get_timestamp():
    return datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
