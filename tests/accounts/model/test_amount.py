#!/usr/bin/env python

import pytest

from dataclasses import FrozenInstanceError
from bank_ddd_es_cqrs.accounts import Amount


def test_amount_immutable():
    amount = Amount(5, 12)
    with pytest.raises(FrozenInstanceError):
        amount.dollars = 4


def test_two_different_objects_same_amount_are_equal():
    amount1 = Amount(5, 43)
    amount2 = Amount(5, 43)
    assert amount1 == amount2


def test_two_different_objects_different_amount_not_equal():
    amount1 = Amount(3, 1)
    amount2 = Amount(6, 32)
    assert amount1 != amount2


def test_greater_if_first_has_more_dollars_and_cents():
    amount1 = Amount(9, 99)
    amount2 = Amount(2, 23)
    assert amount1 > amount2


def test_greater_if_first_has_more_dollars_and_less_cents():
    amount1 = Amount(9, 21)
    amount2 = Amount(2, 23)
    assert amount1 > amount2


def test_greater_if_first_has_less_dollars_more_cents():
    amount1 = Amount(1, 99)
    amount2 = Amount(43, 12)
    assert amount2 > amount1


def test_amount_lower_than_logic():
    amount1 = Amount(1, 98)
    amount2 = Amount(6, 24)
    assert amount1 < amount2


def test_negative_of_amount():
    assert -Amount(50, 24) == Amount(-50, -24)


def test_division_cents_zero_in_divider():
    assert Amount(10, 30) / Amount(2, 0) == Amount(5, 15)


def test_division_dollar_zero_in_divider():
    assert Amount(2, 50) / Amount(0, 10) == Amount(0, 25)


def test_division_cents_zero_in_divided():
    assert Amount(6, 0) / Amount(1, 50) == Amount(4, 0)


def test_division_dollars_zero_in_divided():
    assert Amount(0, 60) / Amount(0, 30) == Amount(0, 2)


def test_division_divider_greater_than_divided():
    assert Amount(1, 50) / Amount(5, 70) == Amount(1, 50)


def test_division_no_zeros():
    assert Amount(50, 80) / Amount(25, 40) == Amount(2, 0)


def test_division_by_zero_dollars_and_cents():
    with pytest.raises(ZeroDivisionError):
        Amount(12, 32) / Amount(0, 0)


def test_greater_even_to():
    amount1 = Amount(50, 23)
    amount2 = Amount(20, 1)
    assert amount1 >= amount2
    amount1 = Amount(20, 44)
    amount2 = Amount(20, 44)
    assert amount1 >= amount2


def test_if_cents_over_100_it_converts_to_dollars():
    amount = Amount(8, 253)
    assert amount.dollars == 10
    assert amount.cents == 53


def test_raises_value_error_when_dividing_by_negative_amount():
    assert Amount(12, 0) / Amount(-3, 0) == Amount(-4, 0)


def test_total_dollars():
    assert Amount(4, 12).total_dollars == 4.12


def test_total_cents():
    assert Amount(9, 42).total_cents == 942
