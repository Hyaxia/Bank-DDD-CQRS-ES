import pytest
from bank_ddd_es_cqrs.accounts import SocialSecurityNumber


def test_social_security_number_throws_app_exception_with_status_422_if_too_much_digits():
    with pytest.raises(ValueError) as e:
        SocialSecurityNumber(1324352351)

