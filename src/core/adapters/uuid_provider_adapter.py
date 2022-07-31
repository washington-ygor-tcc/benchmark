import uuid

from src.core.ports.id_provider_port import IdProviderPort


class UUIDProviderAdapter(IdProviderPort):
    def next_id(self) -> int | str:
        return uuid.uuid1().hex
