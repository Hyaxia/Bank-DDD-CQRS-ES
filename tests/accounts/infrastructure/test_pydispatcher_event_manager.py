from unittest.mock import MagicMock
from bank_ddd_es_cqrs.accounts.infrastructure import PyDispatcherEventManager
from bank_ddd_es_cqrs.accounts.model.events import AccountCreated


def test_subscribed_function_activated_by_event():
    event_to_publish = AccountCreated(
        client_id='asd',
        account_id='asd',
        account_name='gfdgfd',
        operation_id='bgr'
    )
    dummy_sub_func = MagicMock()
    PyDispatcherEventManager.register(dummy_sub_func, AccountCreated)
    PyDispatcherEventManager.publish(event_to_publish)
    dummy_sub_func.assert_called_once()
    dummy_sub_func.assert_called_with(event_to_publish)


def test_multiple_subscribed_functions_called_with_same_data():
    event_to_publish = AccountCreated(
        client_id='asd',
        account_id='asd',
        account_name='gfdgfd',
        operation_id='bgr'
    )
    dummy_sub_func1 = MagicMock()
    dummy_sub_func2 = MagicMock()
    PyDispatcherEventManager.register(dummy_sub_func1, AccountCreated)
    PyDispatcherEventManager.register(dummy_sub_func2, AccountCreated)
    PyDispatcherEventManager.publish(event_to_publish)
    dummy_sub_func1.assert_called_once()
    dummy_sub_func2.assert_called_once()
    dummy_sub_func1.assert_called_with(event_to_publish)
    dummy_sub_func2.assert_called_with(event_to_publish)


