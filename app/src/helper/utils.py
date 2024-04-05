

from typing import Dict, Iterable
import uuid
from enum import Enum
import numpy as np
import pandas as pd


class CanJson(object):
    def to_json_dict(self):
        return self.__dict__

    def dict_keep_items(self, src: Dict, keys: Iterable):
        return {
            k: v
            for k, v in src.items()
            if k in keys
        }


def json_converter(obj):
    if isinstance(obj, CanJson):
        return obj.to_json_dict()

    if isinstance(obj, uuid.UUID):
        return str(obj)

    if isinstance(obj, Enum):
        return obj.value

    if isinstance(obj, pd.Timestamp):
        return str(obj)

    return obj.__dict__
