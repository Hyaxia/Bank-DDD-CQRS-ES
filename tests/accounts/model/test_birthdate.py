import pytest
from bank_ddd_es_cqrs.accounts import Birthdate


def test_birthday_create_from_string_in_right_format():
    Birthdate('27/02/2017')


def test_birthday_throws_app_exception_when_invalid_data_but_right_format():
    with pytest.raises(ValueError) as e:
        Birthdate('50/02/1998')


def test_birthday_has_year_getter():
    b = Birthdate('27/02/2017')
    assert b.year == 2017


def test_birthday_has_month_getter():
    b = Birthdate('27/02/2017')
    assert b.month == 2


def test_birthday_has_day_getter():
    b = Birthdate('27/02/2017')
    assert b.day == 27


def test_birthdate_has_value_getter():
    b = Birthdate('27/02/2017')
    assert b.value == '27/02/2017'


