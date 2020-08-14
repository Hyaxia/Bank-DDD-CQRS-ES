import pytest
import random
from attr import asdict
from flask import Flask
from sqlalchemy.orm.session import Session
from bank_ddd_es_cqrs.shared.model import UniqueID, EventStream
from bank_ddd_es_cqrs.accounts import AccountCreated, AccountCredited, AccountDebited
from bank_ddd_es_cqrs.accounts import PostgresEventStore
from bank_ddd_es_cqrs.accounts import AggregateModel, EventModel, event_store_db, \
    ConcurrencyException, NotFoundException

AGGREGATE_VERSION = 5


@pytest.fixture(scope='module')
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    event_store_db.init_app(app)
    with app.app_context():
        yield app


@pytest.fixture
def account_id():
    return UniqueID()


@pytest.fixture
def client_id():
    return UniqueID()


@pytest.fixture
def db(app, account_id, client_id):
    event_store_db.create_all()

    operation_id = UniqueID()
    account_created_event = AccountCreated(
        operation_id=operation_id.value,
        client_id=client_id.value,
        account_id=account_id.value,
        account_name='test'
    )
    account_credit_event = AccountCredited(
        operation_id=operation_id.value,
        dollars=23, cents=0, account_id=account_id.value
    )

    aggregate = AggregateModel(
        uuid=account_id.value,
        version=AGGREGATE_VERSION
    )

    event1 = EventModel(
        uuid=str(UniqueID()),
        aggregate_uuid=account_id.value,
        name=account_created_event.__class__.__name__,
        data=asdict(account_created_event)
    )
    event2 = EventModel(
        uuid=str(UniqueID()),
        aggregate_uuid=account_id.value,
        name=account_credit_event.__class__.__name__,
        data=asdict(account_credit_event)
    )
    # Add aggregate and event to the db.
    event_store_db.session.add(aggregate)
    event_store_db.session.flush()
    event_store_db.session.add(event1)
    event_store_db.session.commit()
    event_store_db.session.add(event2)
    event_store_db.session.commit()

    yield event_store_db  # this is the object that the tests use

    event_store_db.drop_all()


@pytest.fixture
def session(db) -> Session:
    session = db.session()
    yield session
    session.commit()


@pytest.fixture
def postgres_event_store(session):
    return PostgresEventStore(session)


@pytest.fixture
def credit_event(account_id):
    return AccountCredited(
        dollars=random.randint(50, 100), cents=random.randint(0, 100), account_id=account_id.value,
        operation_id=str(UniqueID())
    )


@pytest.fixture
def debit_event(account_id):
    return AccountDebited(
        dollars=random.randint(20, 30), cents=random.randint(0, 100), account_id=account_id.value,
        operation_id=str(UniqueID())
    )


def test_load_stream_returns_event_stream_of_aggregate(postgres_event_store, account_id):
    event_stream = postgres_event_store.load_stream(account_id.value)
    assert isinstance(event_stream, EventStream)


def test_load_stream_returns_event_stream_where_version_is_right_version(postgres_event_store, account_id):
    event_stream = postgres_event_store.load_stream(account_id)
    assert event_stream.version == AGGREGATE_VERSION


def test_load_stream_returns_two_events(postgres_event_store, account_id):
    event_stream = postgres_event_store.load_stream(account_id)
    assert len(event_stream.events) == 2


def test_load_stream_return_event_stream_where_first_event_is_created_event(postgres_event_store, account_id):
    event_stream = postgres_event_store.load_stream(account_id)
    assert isinstance(event_stream.events[0], AccountCreated)


def test_load_stream_return_event_stream_where_second_event_is_credit_event(postgres_event_store, account_id):
    event_stream = postgres_event_store.load_stream(account_id)
    assert isinstance(event_stream.events[1], AccountCredited)


def test_load_stream_return_credit_event_with_right_amount(postgres_event_store, account_id):
    event_stream = postgres_event_store.load_stream(account_id)
    assert event_stream.events[1].dollars == 23
    assert event_stream.events[1].cents == 0


def test_load_stream_throws_not_found_exception_when_no_aggregate_is_found(postgres_event_store):
    with pytest.raises(NotFoundException):
        postgres_event_store.load_stream(UniqueID())


def test_save_events_adds_events_to_related_aggregate(account_id: UniqueID, session: Session, credit_event,
                                                      debit_event, postgres_event_store):
    postgres_event_store.save_events(aggregate_id=account_id, events=[credit_event, debit_event],
                                     expected_version=AGGREGATE_VERSION)
    aggregate = session.query(AggregateModel).filter(
        AggregateModel.uuid == account_id.value
    ).one()
    assert len(aggregate.events) == 4


def test_save_events_increments_version_by_one_on_successful_save(account_id: UniqueID, session: Session, credit_event,
                                                                  debit_event, postgres_event_store):
    postgres_event_store.save_events(aggregate_id=account_id, events=[credit_event, debit_event],
                                     expected_version=AGGREGATE_VERSION)
    aggregate = session.query(AggregateModel).filter(
        AggregateModel.uuid == account_id.value
    ).one()
    assert aggregate.version == AGGREGATE_VERSION + 1


def test_save_events_throws_concurrency_error_if_version_does_not_match(account_id: UniqueID, session: Session,
                                                                        credit_event, debit_event,
                                                                        postgres_event_store):
    with pytest.raises(ConcurrencyException):
        postgres_event_store.save_events(aggregate_id=account_id, events=[credit_event, debit_event],
                                         expected_version=AGGREGATE_VERSION + 1)


def test_save_events_tries_to_create_new_aggregate_if_no_expected_version_passed(session: Session,
                                                                                 postgres_event_store):
    account_id = UniqueID()
    account_created_event = AccountCreated(
        operation_id=str(UniqueID()),
        client_id=str(UniqueID()),
        account_id=str(account_id),
        account_name='test'
    )
    postgres_event_store.save_events(account_id, [account_created_event])
    found = session.query(AggregateModel).filter(
        AggregateModel.uuid == account_id.value
    ).all()
    assert len(found) == 1


def test_save_events_adds_related_events_to_new_aggregate(session: Session, postgres_event_store):
    account_id = UniqueID()
    account_created_event = AccountCreated(
        operation_id=str(UniqueID()),
        client_id=str(UniqueID()),
        account_id=str(account_id),
        account_name='test'
    )
    credit_event = AccountCredited(
        dollars=22, cents=0, account_id=str(account_id), operation_id=str(UniqueID())
    )
    postgres_event_store.save_events(aggregate_id=account_id, events=[account_created_event, credit_event])
    aggregate = session.query(AggregateModel).filter(
        AggregateModel.uuid == account_id.value
    ).one()
    assert len(aggregate.events) == 2


def test_save_events_passing_expected_version_for_new_aggregate_throws_concurrency_error(session: Session,
                                                                                         postgres_event_store):
    account_id = UniqueID()
    account_created_event = AccountCreated(
        operation_id=str(UniqueID()),
        client_id=str(UniqueID()),
        account_id=str(account_id),
        account_name='test'
    )
    with pytest.raises(ConcurrencyException):
        postgres_event_store.save_events(account_id, [account_created_event], expected_version=6)

