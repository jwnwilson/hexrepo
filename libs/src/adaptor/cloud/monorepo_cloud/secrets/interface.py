from abc import ABC


class SecretAdaptor(ABC):
    def __init__(self) -> None:
        pass

    def get_secret(self, secret_name: str) -> str:
        raise NotImplementedError
