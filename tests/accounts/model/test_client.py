import pytest
from bank_ddd_es_cqrs.accounts import Client, FirstName, LastName, Birthdate, SocialSecurityNumber, \
    ClientCreated, AccountAddedToClient, AccountRemovedFromClient
from bank_ddd_es_cqrs.shared.model import UniqueID


@pytest.fixture
def new_client():
    return Client.create(
        first_name=FirstName("test"),
        last_name=LastName("trt"),
        birthdate=Birthdate('27/02/1998'),
        ssn=SocialSecurityNumber(123456789),
        operation_id=UniqueID()
    )


@pytest.fixture
def new_client_with_account(new_client):
    new_client.add_account(UniqueID(), UniqueID(), 'test')
    return new_client


def test_new_client_has_no_accounts_associated(new_client):
    assert len(new_client.accounts) == 0


def test_add_account_adds_id_to_accounts_property(new_client):
    new_account_id = UniqueID()
    new_client.add_account(new_account_id, UniqueID(), 'test')
    assert new_account_id in new_client.accounts


def test_add_account_produces_account_added_events_with_new_account_id(new_client):
    new_account_id = UniqueID()
    new_client.add_account(new_account_id, UniqueID(), 'test')
    assert isinstance(new_client.uncommitted_changes[-1], AccountAddedToClient)
    assert new_client.uncommitted_changes[-1].account_id == new_account_id.value


def test_creating_new_client_produces_only_client_created_event_to_uncommitted_changes(new_client):
    assert len(new_client.uncommitted_changes) == 1
    assert isinstance(new_client.uncommitted_changes[-1], ClientCreated)


def test_remove_account_remove_account_id_from_accounts_property(new_client_with_account):
    account_id = new_client_with_account.accounts[0]
    new_client_with_account.remove_account(account_id, UniqueID())
    assert len(new_client_with_account.accounts) == 0


def test_remove_account_produces_account_removed_event_with_right_account_id(new_client_with_account):
    account_id = new_client_with_account.accounts[0]
    new_client_with_account.remove_account(account_id, UniqueID())
    assert isinstance(new_client_with_account.uncommitted_changes[-1], AccountRemovedFromClient)
    assert new_client_with_account.uncommitted_changes[-1].account_id == account_id.value
