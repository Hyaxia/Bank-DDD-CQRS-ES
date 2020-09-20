from ...shared.model import UniqueID
from ..composition_root import get_account_write_repo
from ..model.events import AccountAddedToClient
from ..use_cases.account import create_account
# TODO: add here the subscibtions to the events from kafka.
#   We need to create here the event handlers, which will receive the events from kafka, parse them, and pass
#   the needed variables to the use cases.

# TODO: find out a way to use SQLAlchemy inside the event handlers (right now we are getting errors from flask)


def create_added_client_account(event: AccountAddedToClient):
    try:
        with get_account_write_repo() as account_repo:
            create_account(
                operation_id=UniqueID(event.operation_id),
                account_name=event.account_name,
                client_id=UniqueID(event.client_id),
                account_repo=account_repo
            )
    except Exception as e:
        print(e)
