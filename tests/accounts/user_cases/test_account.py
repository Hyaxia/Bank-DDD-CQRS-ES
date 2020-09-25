import pytest
from unittest.mock import Mock, MagicMock
from bank_ddd_es_cqrs.shared.model import UniqueID, EventStream
from bank_ddd_es_cqrs.accounts import Account, AccountCreated, AccountCredited, AccountDebited, Amount, \
    AccountMaximumDebtChanged
from bank_ddd_es_cqrs.accounts import credit_account, debit_account, change_maximum_debt, \
    AmountDTO, create_account


@pytest.fixture
def account_id() -> UniqueID:
    return UniqueID()


def return_based_on_id(account_id):
    def wrapped(target_id):
        if account_id == target_id:
            account_created = AccountCreated(
                operation_id=str(UniqueID()),
                account_id=str(UniqueID()),
                client_id=account_id,
                account_name='test'
            )
            account = Account(EventStream([account_created]))
            account.set_maximum_debt(Amount(500, 0), UniqueID())
            return account
        return None

    return wrapped


@pytest.fixture
def fake_account_repo(account_id):
    repo = Mock()
    repo.get_by_id = MagicMock(side_effect=return_based_on_id(account_id))
    return repo


def test_credit_account_adds_credit_event_to_uncommitted_changes(fake_account_repo, account_id):
    credit_account(UniqueID(), account_id, fake_account_repo, AmountDTO(43, 93))
    account_called_with: Account = fake_account_repo.save.call_args.args[0]
    assert isinstance(account_called_with.uncommitted_changes[-1], AccountCredited)


def test_credit_account_converts_dollars_and_cents_passed_to_amount(fake_account_repo, account_id):
    credit_account(UniqueID(), account_id, fake_account_repo, AmountDTO(50, 24))
    account_called_with: Account = fake_account_repo.save.call_args.args[0]
    credit_event: AccountCredited = account_called_with.uncommitted_changes[-1]
    assert Amount(credit_event.dollars, credit_event.cents) == Amount(50, 24)


def test_credit_account_searches_for_right_account_id(fake_account_repo, account_id):
    credit_account(UniqueID(), account_id, fake_account_repo, AmountDTO(54, 12))
    fake_account_repo.get_by_id.assert_called_with(account_id)


def test_debit_account_adds_debit_event_to_uncommitted_changes(fake_account_repo, account_id):
    debit_account(UniqueID(), account_id, fake_account_repo, AmountDTO(5, 0))
    account_called_with: Account = fake_account_repo.save.call_args.args[0]
    assert isinstance(account_called_with.uncommitted_changes[-1], AccountDebited)


def test_debit_account_searches_for_right_account_id(fake_account_repo, account_id):
    debit_account(UniqueID(), account_id, fake_account_repo, AmountDTO(54, 12))
    fake_account_repo.get_by_id.assert_called_with(account_id)


def test_debit_account_converts_dollars_and_cents_passed_to_amount(fake_account_repo, account_id):
    debit_account(UniqueID(), account_id, fake_account_repo, AmountDTO(99, 12))
    account_called_with: Account = fake_account_repo.save.call_args.args[0]
    debit_event: AccountDebited = account_called_with.uncommitted_changes[-1]
    assert Amount(debit_event.dollars, debit_event.cents) == Amount(99, 12)


def test_set_maximum_debt_adds_maximum_debt_changed_event_to_uncommitted_changes(fake_account_repo, account_id):
    change_maximum_debt(UniqueID(), account_id, fake_account_repo, AmountDTO(1200, 0))
    account_called_with: Account = fake_account_repo.save.call_args.args[0]
    assert isinstance(account_called_with.uncommitted_changes[-1], AccountMaximumDebtChanged)


def test_set_maximum_debt_converts_dollars_and_cents_passed_to_amount(fake_account_repo, account_id):
    debit_account(UniqueID(), account_id, fake_account_repo, AmountDTO(132, 55))
    account_called_with: Account = fake_account_repo.save.call_args.args[0]
    maximum_debt_event: AccountMaximumDebtChanged = account_called_with.uncommitted_changes[-1]
    assert Amount(maximum_debt_event.dollars, maximum_debt_event.cents) == Amount(132, 55)


def test_create_account_first_adds_account_created_to_uncommitted_changes(fake_account_repo):
    create_account(UniqueID(), 'tes', UniqueID(), UniqueID(), fake_account_repo, AmountDTO(90, 0))
    account_called_with: Account = fake_account_repo.save.call_args.args[0]
    assert isinstance(account_called_with.uncommitted_changes[0], AccountCreated)


def test_create_account_events_added_has_the_id_passed_to_the_function(fake_account_repo):
    new_account_client_id = UniqueID()
    create_account(UniqueID(), 'tes', UniqueID(), new_account_client_id, fake_account_repo, AmountDTO(90, 0))
    account_called_with: Account = fake_account_repo.save.call_args.args[0]
    created_event: AccountCreated = account_called_with.uncommitted_changes[0]
    assert created_event.client_id == new_account_client_id.value


def test_create_account_adds_maximum_debt_changed_event_if_amount_specified(fake_account_repo):
    create_account(UniqueID(), 'tes', UniqueID(), UniqueID(), fake_account_repo, AmountDTO(25, 94))
    account_called_with: Account = fake_account_repo.save.call_args.args[0]
    assert isinstance(account_called_with.uncommitted_changes[-1], AccountMaximumDebtChanged)


def test_create_account_does_not_add_maximum_debt_changed_event_if_no_amount_is_specified(fake_account_repo):
    create_account(UniqueID(), 'test', UniqueID(), UniqueID(), fake_account_repo)
    account_called_with: Account = fake_account_repo.save.call_args.args[0]
    assert isinstance(account_called_with.uncommitted_changes[-1], AccountCreated)
