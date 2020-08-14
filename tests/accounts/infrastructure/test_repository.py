from unittest.mock import MagicMock
import pytest
from bank_ddd_es_cqrs.shared.model import UniqueID, EventStream
from bank_ddd_es_cqrs.accounts import ESAccountRepository, ESClientRepository
from bank_ddd_es_cqrs.accounts import Client, Account, SocialSecurityNumber, FirstName, LastName, \
    Birthdate, Amount, AccountCredited, AccountCreated


@pytest.fixture
def fake_event_store():
    return MagicMock()


@pytest.fixture
def account_repo(fake_event_store):
    repo = ESAccountRepository(fake_event_store)
    return repo


@pytest.fixture
def client_repo(fake_event_store):
    repo = ESClientRepository(fake_event_store)
    return repo


@pytest.fixture
def new_client():
    client = Client.create(
        ssn=SocialSecurityNumber(345456567),
        last_name=LastName("test"),
        first_name=FirstName("more"),
        birthdate=Birthdate('23/04/1993'),
        operation_id=UniqueID()
    )
    client.add_account(UniqueID(), UniqueID())
    return client


@pytest.fixture
def new_account():
    account = Account.create(UniqueID(), UniqueID(), UniqueID(), 'test')
    account.set_maximum_debt(Amount(600), UniqueID())
    account.debit(Amount(120), UniqueID())
    account.credit(Amount(700), UniqueID())
    return account


def test_account_repo_save_calls_once_save_events(account_repo, new_account, fake_event_store):
    account_repo.save(new_account)
    fake_event_store.save_events.assert_called_once()


# TODO: this test should work, but the events parameters is changed after it is already called `save_events`
#   because we call the function `mark_changes_as_committed` which clears the events on the aggregate,
#   and for some reason it also changes the parameter inside `assert_called_with`.
# def test_account_repo_passes_right_params_to_save_events(account_repo, new_account, fake_event_store):
#     uncommitted_changes = [*new_account.uncommitted_changes]
#     account_repo.save(new_account)
#     fake_event_store.save_events.assert_called_with(aggregate_id=new_account.account_id, events=uncommitted_changes,
#                                                     expected_version=new_account.version)


def test_after_save_account_has_no_uncommitted_changes(account_repo, new_account):
    account_repo.save(new_account)
    assert len(new_account.uncommitted_changes) == 0


def return_based_on_id(account_id: UniqueID):
    def wrapped(target_id: UniqueID):
        if account_id == target_id:
            return EventStream(
                [
                    AccountCreated(
                        operation_id=str(UniqueID()),
                        client_id=str(UniqueID()),
                        account_id=str(account_id),
                        account_name='test'
                    ),
                    AccountCredited(
                        dollars=20, cents=0, account_id=account_id.value,
                        operation_id=str(UniqueID)
                    )
                ], version=2
            )
        return None

    return wrapped


def test_get_by_id_applies_event_stream(account_repo, fake_event_store):
    account_id = UniqueID()
    fake_event_store.load_stream = MagicMock(side_effect=return_based_on_id(account_id))
    account = account_repo.get_by_id(account_id)
    assert account.balance == Amount(20)
    assert account.version == 2
