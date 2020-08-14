import pytest
from typing import List, Optional
from unittest.mock import patch
from bank_ddd_es_cqrs.shared.model import AggregateRoot, BaseEvent, UniqueID, OperationDuplicate, EventStream


def applyless_aggregate(events: Optional[List[BaseEvent]] = None):
    AggregateRoot.apply = lambda *args, **kwargs: None
    if events:
        aggregate = AggregateRoot(EventStream(events))
    else:
        aggregate = AggregateRoot()
    return aggregate


def test_empty_aggregate_root_start_with_version_minus_one():
    assert applyless_aggregate().version == -1


def test_creating_aggregate_from_stream_sets_version_of_stream_to_aggregate():
    aggregate = AggregateRoot(EventStream([], 5))
    assert aggregate.version == 5


def test_empty_aggregate_root_start_with_no_uncommitted_changes():
    assert len(applyless_aggregate().uncommitted_changes) == 0


def test_initialize_sets_changes():
    aggregate = applyless_aggregate()
    operation_id = UniqueID()
    aggregate._initialize([BaseEvent(operation_id=str(operation_id))])
    assert aggregate.uncommitted_changes[0].operation_id == str(operation_id)


def test_initialize_sets_uncommitted_changes():
    aggregate = applyless_aggregate()
    aggregate._initialize([BaseEvent(operation_id=str(UniqueID())), BaseEvent(operation_id=str(UniqueID()))])
    assert len(aggregate.uncommitted_changes) == 2


def test_mark_changes_as_committed_cleans_uncommitted_changes():
    aggregate = applyless_aggregate()
    aggregate._initialize([BaseEvent(operation_id=str(UniqueID())), BaseEvent(operation_id=str(UniqueID()))])
    aggregate.mark_changes_as_committed()
    assert len(aggregate.uncommitted_changes) == 0


def test_apply_event_is_called_for_each_event_passed_when_loading_aggregate():
    with patch.object(AggregateRoot, 'apply_event') as mock:
        AggregateRoot(EventStream([BaseEvent(operation_id=str(UniqueID())), BaseEvent(operation_id=str(UniqueID())), BaseEvent(operation_id=str(UniqueID()))]))
    assert mock.call_count == 3


def test_applying_new_event_adds_it_to_uncommitted_changes():
    aggregate = applyless_aggregate()
    event = BaseEvent(operation_id=str(UniqueID()))
    aggregate.apply_event(event)
    assert aggregate.uncommitted_changes[-1] == event


def test_loading_aggregate_adds_each_operation_id_to_operations_committed_with_value_of_true():
    event1 = BaseEvent(operation_id=str(UniqueID()))
    aggregate = AggregateRoot(EventStream([event1]))
    assert event1.operation_id in aggregate.committed_operations
    assert aggregate.committed_operations[event1.operation_id] is True


def test_applying_new_events_does_not_add_operation_id_to_operations_committed():
    event1 = BaseEvent(operation_id=str(UniqueID()))
    aggregate = applyless_aggregate()
    aggregate.apply_event(event1)
    assert event1.operation_id not in aggregate.committed_operations


def test_marking_changes_as_committed_adds_committed_events_operation_ids_to_committed_operations():
    aggregate = applyless_aggregate()
    event1 = BaseEvent(operation_id=str(UniqueID()))
    event2 = BaseEvent(operation_id=str(UniqueID()))
    aggregate.apply_event(event1)
    aggregate.apply_event(event2)
    aggregate.mark_changes_as_committed()
    assert event1.operation_id in aggregate.committed_operations
    assert event2.operation_id in aggregate.committed_operations


def test_applying_new_event_with_same_operation_id_as_already_committed_event_raises_app_exception():
    aggregate = applyless_aggregate()
    operation_id = UniqueID()
    event1 = BaseEvent(operation_id=operation_id.value)
    event2 = BaseEvent(operation_id=operation_id.value)
    aggregate.apply_event(event1)
    aggregate.mark_changes_as_committed()
    with pytest.raises(OperationDuplicate):
        aggregate.apply_event(event2)




