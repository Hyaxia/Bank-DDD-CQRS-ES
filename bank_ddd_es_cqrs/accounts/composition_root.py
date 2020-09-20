import os
from contextlib import contextmanager
from .infrastructure import PyDispatcherEventManager, start_kafka_consumer
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


event_manager = PyDispatcherEventManager()
start_kafka_consumer(event_manager.publish, os.environ['ACCOUNTS_KAFKA_CONN_STRING'], os.environ['ACCOUNTS_KAFKA_CDC_TOPIC'], os.environ['ACCOUNTS_KAFKA_CONSUMER_GROUP_ID'])
