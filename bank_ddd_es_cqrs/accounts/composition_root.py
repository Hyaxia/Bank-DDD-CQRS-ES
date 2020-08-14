from contextlib import contextmanager
from .infrastructure import ESAccountRepository, ESClientRepository, PostgresEventStore, sql_session_scope


@contextmanager
def get_account_write_repo() -> ESAccountRepository:
    with sql_session_scope() as session:
        event_store = PostgresEventStore(session)
        yield ESAccountRepository(event_store)


@contextmanager
def get_client_write_repo() -> ESClientRepository:
    with sql_session_scope() as session:
        event_store = PostgresEventStore(session)
        yield ESClientRepository(event_store)
