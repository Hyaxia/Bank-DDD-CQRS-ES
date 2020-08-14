import pytest
from dataclasses import FrozenInstanceError
from bank_ddd_es_cqrs.accounts import AmountDTO, ClientDetailsDTO


def test_amount_dto_immutable():
    amount = AmountDTO(
        dollars=23,
        cents=12
    )
    with pytest.raises(FrozenInstanceError):
        amount.cents = 23


def test_client_details_dto_immutable():
    details = ClientDetailsDTO(
        social_security_number=143123654,
        first_name="gfdg",
        last_name="erwr",
        birthdate="27/02/1998",
    )
    with pytest.raises(FrozenInstanceError):
        details.first_name = 'fdsfdsf'



