from typing import Callable, Type
from .event import BaseEvent
from abc import ABC, abstractmethod


class EventManager(ABC):
    @abstractmethod
    def register(self, func: Callable[[BaseEvent], None], event: Type[BaseEvent]):
        pass

    @abstractmethod
    def publish(self, event: BaseEvent):
        pass
