import pytest
from dataclasses import FrozenInstanceError
from bank_ddd_es_cqrs.accounts import FirstName, LastName


def test_throws_app_exception_when_creating_empty_first_name():
    with pytest.raises(ValueError):
        FirstName("")


def test_throws_app_exception_when_creating_empty_last_name():
    with pytest.raises(ValueError):
        LastName("")


def test_first_name_immutable():
    with pytest.raises(FrozenInstanceError):
        first_name = FirstName('asd')
        first_name.value = 'asd'


def test_last_name_immutable():
    with pytest.raises(FrozenInstanceError):
        first_name = LastName('asd')
        first_name.value = 'asd'

