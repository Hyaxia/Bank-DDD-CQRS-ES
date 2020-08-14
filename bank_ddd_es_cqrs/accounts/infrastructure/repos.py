from .sql import EventStore
from bank_ddd_es_cqrs.shared.model import UniqueID
from ..model import AccountWriteRepository, ClientWriteRepository, Account, Client


class ESAccountRepository(AccountWriteRepository):
    def __init__(self, event_store: EventStore):
        self._event_store = event_store

    def save(self, aggregate_root: Account) -> Account:
        self._event_store.save_events(
            aggregate_id=aggregate_root.account_id,
            events=aggregate_root.uncommitted_changes,
            expected_version=aggregate_root.version
        )
        aggregate_root.mark_changes_as_committed()
        return aggregate_root

    def get_by_id(self, aggregate_id: UniqueID) -> Account:
        event_stream = self._event_store.load_stream(aggregate_id)
        return Account(event_stream)


class ESClientRepository(ClientWriteRepository):
    def __init__(self, event_store: EventStore):
        self._event_store = event_store

    def save(self, aggregate_root: Client) -> Client:
        self._event_store.save_events(
            aggregate_id=aggregate_root.client_id,
            events=aggregate_root.uncommitted_changes,
            expected_version=aggregate_root.version
        )
        aggregate_root.mark_changes_as_committed()
        return aggregate_root

    def get_by_id(self, aggregate_id: UniqueID) -> Client:
        event_stream = self._event_store.load_stream(aggregate_id)
        return Client(event_stream)

