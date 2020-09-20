from ..model.events import AccountAddedToClient
from .account_event_handlers import create_added_client_account


def register_event_handlers(event_manager):
    event_manager.register(create_added_client_account, AccountAddedToClient)
