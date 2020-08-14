from functools import singledispatchmethod
from typing import List, Dict, Optional
from .event import BaseEvent
from .event_stream import EventStream


class OperationDuplicate(Exception):
    def __init__(self) -> None:
        super(OperationDuplicate, self).__init__('Operation has already been performed')


class AggregateRoot:
    def __init__(self, stream: Optional[EventStream] = None) -> None:
        """
        Just a note here, sadly, we cannot avoid inserting the `version` logic into the aggregate root
        although it being an infrastructure detail to protect from concurrency problems (optimistic locking).
        """
        self._version = -1  # Indicates its a new entity
        self._operations: Dict[str, bool] = {}
        if stream:
            self._version = stream.version
            for event in stream.events:
                self.apply_event(event, False)
        self._changes: List[BaseEvent] = []

    def _initialize(self, events: List[BaseEvent]) -> None:
        self._changes = events

    def apply_event(self, event: BaseEvent, is_new: bool = True) -> None:
        self.apply(event)  # type: ignore
        if is_new:
            if self._operation_in_committed_operations(event.operation_id):
                raise OperationDuplicate()
            self._changes.append(event)
        else:
            self._add_operation_id_to_committed(event)

    def _operation_in_committed_operations(self, operation_id: str) -> bool:
        return operation_id in self.committed_operations

    def _add_operation_id_to_committed(self, event: BaseEvent) -> None:
        self._operations[event.operation_id] = True

    @singledispatchmethod
    def apply(self, event: BaseEvent) -> None:
        # TODO: I've tried to use here the ABCMeta and abstractmethod decorator, but it throws exceptions, maybe
        #  I should try it again later and figure out how to remove the errors
        raise NotImplementedError("Not implementation of `apply` available")

    @property
    def uncommitted_changes(self) -> List[BaseEvent]:
        return self._changes

    @property
    def version(self) -> int:
        return self._version

    def mark_changes_as_committed(self) -> None:
        for event in self.uncommitted_changes:
            self._add_operation_id_to_committed(event)
        self._changes.clear()

    @property
    def committed_operations(self) -> Dict[str, bool]:
        return self._operations
