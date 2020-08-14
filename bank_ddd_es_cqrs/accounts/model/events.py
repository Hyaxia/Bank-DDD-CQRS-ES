import attr
from bank_ddd_es_cqrs.shared.model import BaseEvent


@attr.s(frozen=True)
class AccountCreated(BaseEvent):
    client_id: str = attr.ib(kw_only=True)
    account_id: str = attr.ib(kw_only=True)
    account_name: str = attr.ib(kw_only=True)


@attr.s(frozen=True)
class AccountCredited(BaseEvent):
    dollars: int = attr.ib(kw_only=True)
    cents: int = attr.ib(kw_only=True)
    account_id: str = attr.ib(kw_only=True)


@attr.s(frozen=True)
class AccountDebited(BaseEvent):
    dollars: int = attr.ib(kw_only=True)
    cents: int = attr.ib(kw_only=True)
    account_id: str = attr.ib(kw_only=True)


@attr.s(frozen=True)
class AccountMaximumDebtChanged(BaseEvent):
    account_id: str = attr.ib(kw_only=True)
    dollars: int = attr.ib(kw_only=True)
    cents: int = attr.ib(kw_only=True)


@attr.s(frozen=True)
class TransactionCreated(BaseEvent):
    transaction_id: str = attr.ib(kw_only=True)
    account_id_from: str = attr.ib(kw_only=True)
    account_id_to: str = attr.ib(kw_only=True)
    dollars: int = attr.ib(kw_only=True)
    cents: int = attr.ib(kw_only=True)


@attr.s(frozen=True)
class TransactionCompleted(BaseEvent):
    transaction_id: str = attr.ib(kw_only=True)


@attr.s(frozen=True)
class ClientCreated(BaseEvent):
    client_id: str = attr.ib(kw_only=True)
    ssn: int = attr.ib(kw_only=True)
    first_name: str = attr.ib(kw_only=True)
    last_name: str = attr.ib(kw_only=True)
    birthdate: str = attr.ib(kw_only=True)


@attr.s(frozen=True)
class AccountAddedToClient(BaseEvent):
    client_id: str = attr.ib(kw_only=True)
    account_id: str = attr.ib(kw_only=True)
    account_name: str = attr.ib(kw_only=True)


@attr.s(frozen=True)
class AccountRemovedFromClient(BaseEvent):
    client_id: str = attr.ib(kw_only=True)
    account_id: str = attr.ib(kw_only=True)

