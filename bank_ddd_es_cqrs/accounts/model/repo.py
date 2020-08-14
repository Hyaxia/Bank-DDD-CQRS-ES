from typing import TypeVar, Generic
from abc import ABCMeta, abstractmethod
from bank_ddd_es_cqrs.shared.model import UniqueID
from ..model import Account, Client

T = TypeVar('T')


class WriteRepository(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def save(self, aggregate_root: T) -> T:
        pass

    @abstractmethod
    def get_by_id(self, aggregate_id: UniqueID) -> T:
        pass


class AccountWriteRepository(WriteRepository[Account]):
    pass


class ClientWriteRepository(WriteRepository[Client]):
    pass

