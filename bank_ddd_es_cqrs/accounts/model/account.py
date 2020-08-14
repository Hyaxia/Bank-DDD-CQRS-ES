from bank_ddd_es_cqrs.shared.model import AggregateRoot, UniqueID, EventStream
from .events import AccountCreated, AccountDebited, AccountCredited, AccountMaximumDebtChanged
from .amount import Amount


class Account(AggregateRoot):
    @staticmethod
    def create(client_id: UniqueID, account_id: UniqueID, operation_id: UniqueID, account_name: str) -> 'Account':
        """
        This method is used to create new instance of `Account` object.
        The changes to `_changes` and `_version` variables on the new instance
        are so that it will be in an initialized state.
        """
        created_event = AccountCreated(
            account_id=account_id.value,
            client_id=client_id.value,
            account_name=account_name,
            operation_id=operation_id.value
        )
        account = Account(EventStream([created_event]))
        account._initialize([created_event])
        return account

    @AggregateRoot.apply.register
    def _(self, event: AccountCreated) -> None:
        self._account_id = event.account_id
        self._client_id = event.client_id
        self._account_name = event.account_name
        self._balance = Amount(0, 0)
        self._maximum_debt = Amount(0, 0)

    @property
    def client_id(self) -> UniqueID:
        return UniqueID(self._client_id)

    @property
    def account_id(self) -> UniqueID:
        return UniqueID(self._account_id)

    @AggregateRoot.apply.register  # type: ignore
    def _(self, event: AccountDebited) -> None:
        self._balance -= Amount(event.dollars, event.cents)

    @AggregateRoot.apply.register  # type: ignore
    def _(self, event: AccountCredited) -> None:
        self._balance += Amount(event.dollars, event.cents)

    @AggregateRoot.apply.register  # type: ignore
    def _(self, event: AccountMaximumDebtChanged) -> None:
        self._maximum_debt = Amount(event.dollars, event.cents)

    def credit(self, amount: Amount, operation_id: UniqueID) -> None:
        self.apply_event(AccountCredited(
            operation_id=operation_id.value,
            dollars=amount.dollars,
            cents=amount.cents,
            account_id=self.account_id.value
        ))

    def debit(self, amount: Amount, operation_id: UniqueID) -> None:
        """
        Invariants:
            - We check that the debit that we want to perform wont make the balance go below the maximum debt
        """
        if (self._balance - amount) < - self.maximum_debt:
            raise ValueError(
                f'Trying to debit {amount} from balance of {self.balance} while maximum debt is {self.maximum_debt}',
            )
        self.apply_event(AccountDebited(
            operation_id=operation_id.value,
            dollars=amount.dollars,
            cents=amount.cents,
            account_id=self.account_id.value
        ))

    @property
    def balance(self) -> Amount:
        return self._balance

    @property
    def maximum_debt(self) -> Amount:
        return self._maximum_debt

    def set_maximum_debt(self, amount: Amount, operation_id: UniqueID) -> None:
        """
        Invariants:
            - Maximum debt amount cannot be lower than 0, we look at it as a positive value
            - If balance is negative, we check that the `maximum_debt` wont be lower than the negative of the balance
        """
        if amount < Amount(0, 0):
            raise ValueError(f'Maximum debt amount cannot be lower than 0, tried to set {amount}')
        if self.balance < Amount(0, 0):
            if - self.balance > amount:
                raise ValueError(f'Trying to set maximum debt to {amount} while current balance is {self.balance}')
        self.apply_event(
            AccountMaximumDebtChanged(
                operation_id=operation_id.value,
                account_id=self.account_id.value,
                dollars=amount.dollars,
                cents=amount.cents
            ))
