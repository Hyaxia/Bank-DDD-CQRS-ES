from typing import List
from .first_last_name import FirstName, LastName
from .social_security_number import SocialSecurityNumber
from .birthdate import Birthdate
from .events import ClientCreated, AccountAddedToClient, AccountRemovedFromClient
from bank_ddd_es_cqrs.shared.model import AggregateRoot, UniqueID, EventStream


class Client(AggregateRoot):
    @staticmethod
    def create(ssn: SocialSecurityNumber, first_name: FirstName, last_name: LastName, birthdate: Birthdate,
               operation_id: UniqueID) -> 'Client':
        created_event = ClientCreated(
            client_id=str(UniqueID()),
            ssn=ssn.value,
            first_name=first_name.value,
            last_name=last_name.value,
            birthdate=birthdate.value,
            operation_id=operation_id.value
        )
        client = Client(EventStream([created_event]))
        client._initialize([created_event])
        return client

    @AggregateRoot.apply.register
    def _(self, event: ClientCreated) -> None:
        self._client_id: UniqueID = UniqueID(event.client_id)
        self._ssn: SocialSecurityNumber = SocialSecurityNumber(event.ssn)
        self._first_name: FirstName = FirstName(event.first_name)
        self._last_name: LastName = LastName(event.last_name)
        self._birthdate: Birthdate = Birthdate(event.birthdate)
        self._accounts: List[UniqueID] = []

    @AggregateRoot.apply.register  # type: ignore
    def _(self, event: AccountAddedToClient) -> None:
        self._accounts.append(UniqueID(event.account_id))

    @AggregateRoot.apply.register  # type: ignore
    def _(self, event: AccountRemovedFromClient) -> None:
        self._accounts.remove(UniqueID(event.account_id))

    @property
    def client_id(self) -> UniqueID:
        return self._client_id

    @property
    def ssn(self) -> SocialSecurityNumber:
        return self._ssn

    @property
    def first_name(self) -> FirstName:
        return self._first_name

    @property
    def last_name(self) -> LastName:
        return self._last_name

    @property
    def birthdate(self) -> Birthdate:
        return self._birthdate

    @property
    def accounts(self) -> List[UniqueID]:
        return self._accounts

    def add_account(self, account_id: UniqueID, operation_id: UniqueID, account_name: str) -> None:
        self.apply_event(AccountAddedToClient(
            client_id=self.client_id.value,
            account_id=account_id.value,
            operation_id=operation_id.value,
            account_name=account_name
        ))

    def remove_account(self, account_id: UniqueID, operation_id: UniqueID) -> None:
        if account_id not in self.accounts:
            raise ValueError(f'Account {account_id} is not connected to in client {self.client_id}')
        self.apply_event(AccountRemovedFromClient(
            client_id=self.client_id.value,
            account_id=account_id.value,
            operation_id=operation_id.value
        ))
