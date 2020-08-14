from attr import asdict
from typing import List, Type, Optional
from abc import ABC, abstractmethod
from sqlalchemy.orm.session import Session  # type: ignore
from ...model import events as account_module_events
from bank_ddd_es_cqrs.shared.model import BaseEvent, EventStream, UniqueID, AppException, StatusCodes
from .model import AggregateModel, EventModel


class ConcurrencyException(AppException):
    def __init__(self, msg: str) -> None:
        super(ConcurrencyException, self).__init__(msg, StatusCodes.CONFLICT_WITH_CURRENT_STATE.value)


class NotFoundException(AppException):
    def __init__(self, msg: str) -> None:
        super(NotFoundException, self).__init__(msg, StatusCodes.NOT_FOUND.value)


class EventStore(ABC):
    @abstractmethod
    def save_events(self, aggregate_id: UniqueID, events: List[BaseEvent], expected_version: int) -> None:
        pass

    @abstractmethod
    def load_stream(self, aggregate_id: UniqueID) -> EventStream:
        pass


class PostgresEventStore(EventStore):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session: Session = session

    def load_stream(self, aggregate_id: UniqueID) -> EventStream:
        aggregate = self.session.query(AggregateModel).filter(
            AggregateModel.uuid == str(aggregate_id)
        ).first()

        if not aggregate:
            raise NotFoundException(f'No aggregate with id {aggregate_id}')

        # translate all events models to proper event objects (see part 1)
        events_objects = [self._event_model_to_core(model) for model in aggregate.events]
        version = aggregate.version

        return EventStream(events_objects, version)

    def _event_model_to_core(self, event_model: EventModel) -> BaseEvent:
        class_name = event_model.name
        kwargs = event_model.data
        event_class: Type[BaseEvent] = getattr(account_module_events, class_name)
        return event_class(**kwargs)

    def save_events(self, aggregate_id: UniqueID, events: List[BaseEvent],
                    expected_version: Optional[int] = None) -> None:
        if expected_version and expected_version != -1:
            self._update_aggregate_version_check(aggregate_id, expected_version)
        else:
            self._create_aggregate(aggregate_id)
        for event in events:
            self.session.add(
                EventModel(
                    uuid=str(UniqueID()),
                    aggregate_uuid=str(aggregate_id),
                    name=event.__class__.__name__,
                    data=asdict(event)
                )
            )

    def _create_aggregate(self, aggregate_id: UniqueID) -> None:
        aggregate = AggregateModel(uuid=str(aggregate_id))
        self.session.add(aggregate)

    def _update_aggregate_version_check(self, aggregate_id: UniqueID, expected_version: Optional[int]) -> None:
        aggregates = self.session.query(AggregateModel).filter(
            (AggregateModel.version == expected_version) &
            (AggregateModel.uuid == str(aggregate_id))
        ).all()
        if len(aggregates) != 1:
            raise ConcurrencyException(f'Found no aggregate with id {aggregate_id} and version {expected_version}')
        target_aggregate = aggregates[0]
        target_aggregate.version = expected_version + 1
