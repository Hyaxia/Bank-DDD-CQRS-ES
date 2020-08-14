from typing import List
from .event import BaseEvent
from dataclasses import dataclass, field


@dataclass(frozen=True)
class EventStream:
    events: List[BaseEvent]
    version: int = field(default=-1)

