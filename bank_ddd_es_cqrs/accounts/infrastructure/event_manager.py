from typing import Type, Callable, Any
from pydispatch import dispatcher
from bank_ddd_es_cqrs.shared.model import EventManager, BaseEvent


class PyDispatcherEventManager(EventManager):
    @classmethod
    def register(cls, func: Callable[[BaseEvent], None], event: Type[BaseEvent]):
        def wrapper(signal, sender):
            func(sender)

        dispatcher.connect(
            wrapper,
            signal=event.__name__,
            sender=dispatcher.Any,
            weak=False
        )

    @classmethod
    def publish(cls, event: BaseEvent):
        dispatcher.send(
            signal=event.__class__.__name__,
            sender=event
        )
