from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic
from .unique_id import UniqueID

T = TypeVar('T')


class WriteRepository(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def save(self, aggregate_root: T) -> T:
        pass

    @abstractmethod
    def get_by_id(self, aggregate_id: UniqueID) -> T:
        pass
