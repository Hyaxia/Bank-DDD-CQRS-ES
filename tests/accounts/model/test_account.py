import random
import pytest
from bank_ddd_es_cqrs.accounts import Account, AccountCreated, Amount, AccountCredited, AccountDebited, \
    AccountMaximumDebtChanged
from bank_ddd_es_cqrs.shared.model import UniqueID, EventStream


@pytest.fixture
def new_random_account():
    account = Account.create(UniqueID(), UniqueID(), UniqueID(), 'test')
    return account


@pytest.fixture
def new_random_account_with_high_maximum_debt():
    account = Account.create(UniqueID(), UniqueID(), UniqueID(), 'test')
    account.set_maximum_debt(Amount(500, 24), UniqueID())
    return account


@pytest.fixture
def new_random_account_unlimited_debt():
    account = Account.create(UniqueID(), UniqueID(), UniqueID(), 'test')
    account.set_maximum_debt(Amount(999999999999999, 0), UniqueID())
    return account


@pytest.fixture
def related_random_account_created_event(new_random_account):
    return AccountCreated(
        client_id=new_random_account.client_id.value,
        account_id=new_random_account.account_id.value,
        operation_id=new_random_account.uncommitted_changes[-1].operation_id,
        account_name='test'
    )


@pytest.fixture
def new_random_account_credit_event(new_random_account):
    amount = Amount(random.randint(0, 9999), random.randint(0, 300))
    return AccountCredited(
        dollars=amount.dollars,
        cents=amount.cents,
        account_id=new_random_account.account_id.value,
        operation_id=str(UniqueID())
    )


@pytest.fixture
def new_random_account_debit_event(new_random_account):
    amount = Amount(random.randint(0, 9999), random.randint(0, 300))
    return AccountDebited(
        dollars=amount.dollars,
        cents=amount.cents,
        account_id=new_random_account.account_id.value,
        operation_id=str(UniqueID())
    )


def get_account_credited_event(account_id, amount: Amount):
    return AccountCredited(
        dollars=amount.dollars,
        cents=amount.cents,
        account_id=account_id.value,
        operation_id=str(UniqueID())
    )


def test_creating_account_produces_account_created_event(new_random_account, related_random_account_created_event):
    uncommitted = new_random_account.uncommitted_changes
    assert len(uncommitted) == 1
    assert uncommitted[0] == related_random_account_created_event


def test_create_function_returns_new_account():
    account = Account.create(UniqueID(), UniqueID(), UniqueID(), 'test')
    assert isinstance(account, Account)


def test_created_account_has_balance_of_zero(new_random_account):
    assert new_random_account.balance == Amount(0, 0)


def test_created_account_has_maximum_debt_of_zero(new_random_account):
    assert new_random_account.maximum_debt == Amount(0, 0)


def test_loading_account_with_only_created_event_has_zero_balance(related_random_account_created_event):
    account = Account(EventStream([related_random_account_created_event]))
    assert account.balance == Amount(0, 0)


def test_loading_account_from_created_and_credited_events_adds_to_balance(new_random_account,
                                                                          related_random_account_created_event):
    credited_event = get_account_credited_event(new_random_account.account_id, Amount(50, 42))
    account = Account(EventStream([related_random_account_created_event, credited_event]))
    assert account.balance == Amount(50, 42)


def test_loading_account_from_created_credited_debited_adds_to_balance(
    new_random_account,
    related_random_account_created_event,
    new_random_account_credit_event,
    new_random_account_debit_event
):
    account = Account(EventStream([
        related_random_account_created_event, new_random_account_credit_event, new_random_account_debit_event
    ]))
    amount_credit = Amount(new_random_account_credit_event.dollars, new_random_account_credit_event.cents)
    amount_debit = Amount(new_random_account_debit_event.dollars, new_random_account_debit_event.cents)
    final = amount_credit - amount_debit
    assert account.balance == final


def test_credit_increases_balance(related_random_account_created_event):
    account = Account(EventStream([related_random_account_created_event]))
    account.credit(Amount(120, 65), UniqueID())
    assert account.balance == Amount(120, 65)


def test_credit_adds_account_credited_event_to_uncommitted_changes(new_random_account,
                                                                   related_random_account_created_event,
                                                                   new_random_account_credit_event):
    account = Account(EventStream([related_random_account_created_event]))
    amount = Amount(new_random_account_credit_event.dollars, new_random_account_credit_event.cents)
    account.credit(amount, UniqueID(new_random_account_credit_event.operation_id))
    assert account.uncommitted_changes[-1] == new_random_account_credit_event


def test_debit_decreases_balance(new_random_account_unlimited_debt):
    new_random_account_unlimited_debt.debit(Amount(25, 12), UniqueID())
    assert new_random_account_unlimited_debt.balance == Amount(-25, -12)


def test_debit_adds_account_debited_event_to_uncommitted_changes(
    new_random_account_unlimited_debt,
    new_random_account_debit_event
):
    amount = Amount(new_random_account_debit_event.dollars, new_random_account_debit_event.cents)
    new_random_account_unlimited_debt.debit(amount, UniqueID())
    assert isinstance(new_random_account_unlimited_debt.uncommitted_changes[-1], AccountDebited)


def test_new_account_has_version_minus_one(new_random_account):
    assert new_random_account.version == -1


def test_new_account_has_default_maximum_debt(new_random_account):
    assert isinstance(new_random_account.maximum_debt, Amount)


def test_account_maximum_debt_cannot_be_lower_than_0():
    with pytest.raises(ValueError):
        account = Account.create(UniqueID(), UniqueID(), UniqueID(), 'test')
        account.set_maximum_debt(Amount(-100, -65), UniqueID())


def test_debit_over_maximum_debt_raises_maximum_debt_reached(new_random_account):
    with pytest.raises(ValueError):
        new_random_account.debit(
            new_random_account.maximum_debt + Amount(10, 12), UniqueID()
        )


def test_setting_maximum_debt_changes_maximum_debt(new_random_account):
    new_random_account.set_maximum_debt(Amount(500, 54), UniqueID())
    assert new_random_account.maximum_debt == Amount(500, 54)


def test_maximum_debt_cannot_be_lower_than_balance(new_random_account_with_high_maximum_debt):
    new_random_account_with_high_maximum_debt.debit(
        new_random_account_with_high_maximum_debt.maximum_debt / Amount(2, 0), UniqueID()
    )
    with pytest.raises(ValueError):
        new_random_account_with_high_maximum_debt.set_maximum_debt(
            new_random_account_with_high_maximum_debt.maximum_debt / Amount(
                3, 0), UniqueID())


def test_maximum_debt_set_when_balance_is_positive(new_random_account):
    new_random_account.credit(Amount(666, 67), UniqueID())
    new_random_account.set_maximum_debt(Amount(60, 0), UniqueID())


def test_setting_maximum_debt_appends_event(new_random_account):
    new_random_account.set_maximum_debt(Amount(5000, 12), UniqueID())
    assert isinstance(new_random_account.uncommitted_changes[-1], AccountMaximumDebtChanged)


def test_mark_changes_as_committed_removes_events_from_uncommitted_changes(new_random_account):
    assert len(new_random_account.uncommitted_changes) != 0
    new_random_account.mark_changes_as_committed()
    assert len(new_random_account.uncommitted_changes) == 0
