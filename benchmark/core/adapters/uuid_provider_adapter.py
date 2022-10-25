import uuid

from benchmark.core.ports import IdProviderPort

__all__ = ["UUIDProviderAdapter"]


class UUIDProviderAdapter(IdProviderPort):
    def next_id(self) -> int | str:
        return uuid.uuid1().hex
