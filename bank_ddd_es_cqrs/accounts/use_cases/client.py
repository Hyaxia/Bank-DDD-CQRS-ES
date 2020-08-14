from .dto import ClientDetailsDTO
from bank_ddd_es_cqrs.shared.model import UniqueID
from ..model import Client, ClientWriteRepository, FirstName, LastName, SocialSecurityNumber, Birthdate


def create_client(operation_id: UniqueID, details: ClientDetailsDTO, repo: ClientWriteRepository) -> UniqueID:
    client = Client.create(
        ssn=SocialSecurityNumber(details.social_security_number),
        first_name=FirstName(details.first_name),
        last_name=LastName(details.last_name),
        birthdate=Birthdate(details.birthdate),
        operation_id=operation_id
    )
    repo.save(client)
    return client.client_id


def add_account_to_client(operation_id: UniqueID, client_id: UniqueID, repo: ClientWriteRepository,
                          new_account_name: str) -> UniqueID:
    client = repo.get_by_id(client_id)
    new_account_id = UniqueID()
    client.add_account(
        account_name=new_account_name,
        account_id=new_account_id,
        operation_id=operation_id
    )
    repo.save(client)
    return new_account_id


def remove_account_from_client(operation_id: UniqueID, client_id: UniqueID, account_id: UniqueID,
                               repo: ClientWriteRepository) -> None:
    client = repo.get_by_id(client_id)
    client.remove_account(account_id, operation_id)
    repo.save(client)
