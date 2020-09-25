from ...shared.model import UniqueID
from ..composition_root import get_account_write_repo
from ..model.events import AccountAddedToClient
from ..use_cases.account import create_account


def create_added_client_account(event: AccountAddedToClient):
    try:
        with get_account_write_repo() as account_repo:
            create_account(
                operation_id=UniqueID(event.operation_id),
                account_name=event.account_name,
                account_id=UniqueID(event.account_id),
                client_id=UniqueID(event.client_id),
                account_repo=account_repo
            )
    except Exception as e:
        print('Error creating clinet account', e)
