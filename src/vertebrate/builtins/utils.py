"""
Shared helper objects.
"""

import re
from typing import Any

from vertebrate.data import Address


def format_address(address: Address) -> str:
    return re.sub('[^a-zA-Z0-9]', '_', address).strip('_')


class ObjectByAddress(object):

    def __init__(self, dict_: dict[str, Any]):
        self.dict_ = dict_

    def __getitem__(self, address: Address) -> type:
        return self.dict_[format_address(address)]

    def __setitem__(self, address: Address, obj: Any) -> None:
        self.dict_[format_address(address)] = obj
