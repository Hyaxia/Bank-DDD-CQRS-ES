# TODO: the event manager should have a 'subscribe' handler to handle any function that wants to consume an event from kafka.
# TODO: I need to perform the changes in such a way that the version stays as it should.
#   Because we have multiple instances which read the data from kafka, we need to be carefull about the order
#   of the events. Maybe there is a way to tell kafka-connect to send the messages according some hash function
#   that is executed on the aggregate id, and this way only one instance of the server will read each aggregate.
#   This way, will have much less problems.
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
