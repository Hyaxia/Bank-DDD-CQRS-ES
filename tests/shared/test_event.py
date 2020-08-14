import pytest
from bank_ddd_es_cqrs.shared.model import BaseEvent


def test_event_default_version_is_one():
    assert BaseEvent(operation_id='asd').version == 1


def test_event_construct_from_dict():
    BaseEvent(**{'version': 1, 'operation_id': 'fdsf'})


def test_event_construct_from_dict_changes_version():
    event = BaseEvent(**{'version': 4, 'operation_id': 'fdsf'})
    assert event.version == 4


def test_event_is_key_word_only():
    with pytest.raises(TypeError):
        BaseEvent('operation')
    with pytest.raises(TypeError):
        BaseEvent('operation', version=3)

