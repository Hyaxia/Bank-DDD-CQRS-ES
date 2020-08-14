import pytest
from dataclasses import FrozenInstanceError
from bank_ddd_es_cqrs.shared.model import EventStream


def test_default_version_on_new_event_stream_is_minus_one():
    event_stream = EventStream([])
    assert event_stream.version == -1


def test_event_stream_immutable():
    event_stream = EventStream([])
    with pytest.raises(FrozenInstanceError):
        event_stream.version = 2
    with pytest.raises(FrozenInstanceError):
        event_stream.events = ['asd']



