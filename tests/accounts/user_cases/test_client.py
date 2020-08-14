import pytest
from unittest.mock import Mock, MagicMock
from bank_ddd_es_cqrs.shared.model import UniqueID, EventStream
from bank_ddd_es_cqrs.accounts import create_client, ClientDetailsDTO, add_account_to_client, \
    remove_account_from_client
from bank_ddd_es_cqrs.accounts import Client, ClientCreated, SocialSecurityNumber, FirstName, LastName, \
    Birthdate, AccountAddedToClient, AccountRemovedFromClient


@pytest.fixture
def client_id() -> UniqueID:
    return UniqueID()


@pytest.fixture
def account_id() -> UniqueID:
    return UniqueID()


def return_based_on_id(client_id):
    def wrapped(target_id):
        if client_id == target_id:
            client_created = ClientCreated(
                operation_id=str(UniqueID()),
                client_id=client_id.value,
                ssn=SocialSecurityNumber(123456789).value,
                first_name=FirstName('asd').value,
                last_name=LastName('asd').value,
                birthdate=Birthdate('22/01/1900').value
            )
            client = Client(EventStream([client_created]))
            return client
        return None

    return wrapped


def return_based_on_id_with_account(client_id, account_id):
    def wrapper(target_id):
        client = return_based_on_id(client_id)(target_id)
        if client:
            client.add_account(account_id, UniqueID(), 'test')
            client.mark_changes_as_committed()
            return client
        return None

    return wrapper


@pytest.fixture
def fake_client_repo(client_id):
    repo = Mock()
    repo.get_by_id = MagicMock(side_effect=return_based_on_id(client_id))
    return repo


@pytest.fixture
def fake_client_repo_with_accounts(client_id, account_id):
    repo = Mock()
    repo.get_by_id = MagicMock(side_effect=return_based_on_id_with_account(client_id, account_id))
    return repo


def test_create_client_adds_created_event_to_uncommitted_changes(fake_client_repo):
    create_client(UniqueID(), ClientDetailsDTO(
        social_security_number=123543234,
        first_name="asd",
        last_name="fdsf",
        birthdate="12/04/2012"
    ), fake_client_repo)
    account_called_with: Client = fake_client_repo.save.call_args.args[0]
    assert isinstance(account_called_with.uncommitted_changes[-1], ClientCreated)


def test_add_account_for_client_adds_account_added_to_uncommitted_changes(fake_client_repo, client_id):
    add_account_to_client(UniqueID(), client_id, fake_client_repo, 'test')
    account_called_with: Client = fake_client_repo.save.call_args.args[0]
    assert isinstance(account_called_with.uncommitted_changes[-1], AccountAddedToClient)


def test_remove_account_for_client_adds_removed_account_event_to_uncommitted_changes(fake_client_repo_with_accounts,
                                                                                     client_id,
                                                                                     account_id):
    remove_account_from_client(UniqueID(), client_id, account_id, fake_client_repo_with_accounts)
    account_called_with: Client = fake_client_repo_with_accounts.save.call_args.args[0]
    assert isinstance(account_called_with.uncommitted_changes[-1], AccountRemovedFromClient)
