import json
import pytest
from attr import asdict
from flask.testing import FlaskClient
from sqlalchemy.orm.session import Session
from bank_ddd_es_cqrs.accounts.app import account_app_factory
from bank_ddd_es_cqrs.accounts import AggregateModel, EventModel, event_store_db
from bank_ddd_es_cqrs.shared.model import UniqueID
from bank_ddd_es_cqrs.accounts import AccountCreated, AccountCredited, ClientCreated, \
    SocialSecurityNumber, FirstName, LastName, Birthdate, AccountAddedToClient

AGGREGATE_VERSION = 5


@pytest.fixture
def account_name() -> str:
    return 'test'


@pytest.fixture
def account_id() -> UniqueID:
    return UniqueID()


@pytest.fixture
def client_id() -> UniqueID:
    return UniqueID()


@pytest.fixture
def app():
    return account_app_factory("sqlite:///:memory:")


@pytest.fixture
def fake_app(app) -> FlaskClient:
    with app.test_client() as c:
        yield c


@pytest.fixture
def db(app, account_id: UniqueID, client_id: UniqueID, account_name: str):
    with app.app_context():
        event_store_db.create_all()

        client_create_operation_id = UniqueID()
        client_created_event = ClientCreated(
            client_id=str(client_id), ssn=SocialSecurityNumber(123456789).value,
            operation_id=str(client_create_operation_id),
            first_name=FirstName('test').value, last_name=LastName('test').value,
            birthdate=Birthdate('27/02/1998').value
        )
        account_added_to_client = AccountAddedToClient(client_id=str(client_id), account_id=str(account_id),
                                                       operation_id=str(client_create_operation_id),
                                                       account_name=account_name)

        account_create_operation_id = UniqueID()
        account_created_event = AccountCreated(
            operation_id=account_create_operation_id.value,
            client_id=str(client_id),
            account_id=str(account_id),
            account_name=account_name
        )
        account_credit_event = AccountCredited(
            operation_id=account_create_operation_id.value,
            dollars=23, cents=0, account_id=str(account_id)
        )

        client_aggregate = AggregateModel(
            uuid=str(client_id),
            version=AGGREGATE_VERSION
        )
        client_created_db_event = EventModel(
            uuid=str(UniqueID()),
            aggregate_uuid=str(client_id),
            name=client_created_event.__class__.__name__,
            data=asdict(client_created_event)
        )
        account_added_to_client_db_event = EventModel(
            uuid=str(UniqueID()),
            aggregate_uuid=str(client_id),
            name=account_added_to_client.__class__.__name__,
            data=asdict(account_added_to_client)
        )

        account_aggregate = AggregateModel(
            uuid=str(account_id),
            version=AGGREGATE_VERSION
        )
        account_created_db_event = EventModel(
            uuid=str(UniqueID()),
            aggregate_uuid=account_id.value,
            name=account_created_event.__class__.__name__,
            data=asdict(account_created_event)
        )
        account_credited_db_event = EventModel(
            uuid=str(UniqueID()),
            aggregate_uuid=account_id.value,
            name=account_credit_event.__class__.__name__,
            data=asdict(account_credit_event)
        )

        event_store_db.session.add(client_aggregate)
        event_store_db.session.add(account_aggregate)
        event_store_db.session.flush()
        event_store_db.session.add(client_created_db_event)
        event_store_db.session.add(account_added_to_client_db_event)
        event_store_db.session.add(account_created_db_event)
        event_store_db.session.add(account_credited_db_event)
        event_store_db.session.commit()

        yield event_store_db  # this is the object that the tests use

        event_store_db.drop_all()


@pytest.fixture
def session(db) -> Session:
    session = db.session()
    yield session
    session.commit()


def test_credit_account_adds_credit_event_to_db(fake_app: FlaskClient, db, account_id: UniqueID, session: Session):
    fake_app.patch(
        f'/api/v1/account/{account_id}/balance',
        data=json.dumps({
            'action': 'credit',
            'dollars': 50,
            'cents': 12
        }),
        content_type='application/json'
    )
    aggregate = session.query(AggregateModel).filter(
        AggregateModel.uuid == account_id.value
    ).one()
    assert aggregate.events[-1].data['dollars'] == 50
    assert aggregate.events[-1].data['cents'] == 12
    assert aggregate.version == AGGREGATE_VERSION + 1


def test_debit_account_adds_credit_event_to_db(fake_app: FlaskClient, db, account_id, session: Session):
    fake_app.patch(
        f'/api/v1/account/{account_id}/balance',
        data=json.dumps({
            'action': 'debit',
            'dollars': 12,
            'cents': 95
        }),
        content_type='application/json'
    )
    aggregate = session.query(AggregateModel).filter(
        AggregateModel.uuid == account_id.value
    ).one()
    assert aggregate.events[-1].data['dollars'] == 12
    assert aggregate.events[-1].data['cents'] == 95
    assert aggregate.version == AGGREGATE_VERSION + 1


def test_credit_account_invalid_data_returns_status_400(fake_app, account_id):
    result = fake_app.patch(
        f'/api/v1/account/{account_id}/balance',
        data=json.dumps({
            'action': 'credit',
            'invalidKey': {
                'dollars': 50,
                'cents': 12
            }
        }),
        content_type='application/json'
    )
    assert result._status_code == 400


def test_add_account_creates_account_added_to_client_event(fake_app: FlaskClient, db, client_id, account_id,
                                                           session: Session):
    fake_app.post(
        f'/api/v1/client/{client_id}/account',
        data=json.dumps({
            'account_name': 'test',
        }),
        content_type='application/json'
    )
    aggregate = session.query(AggregateModel).filter(
        AggregateModel.uuid == str(client_id)
    ).one()
    assert aggregate.events[-1].name == 'AccountAddedToClient'
    assert aggregate.events[-1].data['client_id'] == str(client_id)


def test_add_account_returns_201(fake_app: FlaskClient, db, client_id, account_id, session: Session):
    result = fake_app.post(
        f'/api/v1/client/{client_id}/account',
        data=json.dumps({
            'account_name': 'test',
        }),
        content_type='application/json'
    )
    assert result._status_code == 201


def test_add_account_adds_location_header_to_response(fake_app: FlaskClient, db, client_id, account_id,
                                                      session: Session):
    result = fake_app.post(
        f'/api/v1/client/{client_id}/account',
        data=json.dumps({
            'account_name': 'test',
        }),
        content_type='application/json'
    )
    for header in result.headers:
        if header[0] is 'Location':
            return
    raise Exception('no `Location` header was found`')


def test_add_account_to_non_existing_account_returns_404(fake_app: FlaskClient, db, client_id, account_id,
                                                         session: Session):
    result = fake_app.post(
        f'/api/v1/client/test_not_found/account',
        data=json.dumps({
            'account_name': 'test',
        }),
        content_type='application/json'
    )
    assert result._status_code == 404


def test_add_account_with_wrong_payload_returns_400(fake_app: FlaskClient, db, client_id, account_id, session: Session):
    result = fake_app.post(
        f'/api/v1/client/{client_id}/account',
        data=json.dumps({
            'wrong_key': 'test',
        }),
        content_type='application/json'
    )
    assert result._status_code == 400


def test_create_client_returns_201(fake_app: FlaskClient, db, client_id, account_id, session: Session):
    result = fake_app.post(
        f'/api/v1/client',
        data=json.dumps({
            'first_name': 'my name',
            'last_name': 'my last name',
            'birth_date': '27/02/1998',
            'social_security_number': 123456789
        }),
        content_type='application/json'
    )
    assert result._status_code == 201


def test_create_client_creates_new_client_created_event(fake_app: FlaskClient, db, client_id, account_id,
                                                        session: Session):
    result = fake_app.post(
        f'/api/v1/client',
        data=json.dumps({
            'first_name': 'my name',
            'last_name': 'my last name',
            'birth_date': '27/02/1998',
            'social_security_number': 123456789
        }),
        content_type='application/json'
    )
    new_client_id = None
    for header in result.headers:
        if header[0] is 'Location':
            new_client_id = header[1].split('/')[-1]
            break
    if not new_client_id:
        raise Exception('no new client was found')
    aggregate = session.query(AggregateModel).filter(
        AggregateModel.uuid == new_client_id
    ).one()
    assert aggregate.events[-1].name == 'ClientCreated'
    assert aggregate.events[-1].data['client_id'] == new_client_id


def test_create_client_with_wrong_payload_structure_returns_400(fake_app: FlaskClient, db, client_id, account_id,
                                                                session: Session):
    result = fake_app.post(
        f'/api/v1/client',
        data=json.dumps({
            'first_name': 'my name',
            'last_name': 'my last name',
            'birth_date': '27/02/1998',
        }),
        content_type='application/json'
    )
    assert result._status_code == 400


def test_create_client_with_wrong_payload_field_value_returns_400(fake_app: FlaskClient, db, client_id, account_id,
                                                                  session: Session):
    result = fake_app.post(
        f'/api/v1/client',
        data=json.dumps({
            'first_name': 'my name',
            'last_name': 'my last na',
            'birth_date': '27/02/1998',
            'social_security_number': 12345
        }),
        content_type='application/json'
    )
    assert result._status_code == 422
