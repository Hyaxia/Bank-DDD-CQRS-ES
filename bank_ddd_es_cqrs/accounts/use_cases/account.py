from typing import Optional
from bank_ddd_es_cqrs.shared.model import UniqueID
from ..model import AccountWriteRepository, Amount, Account
from .dto import AmountDTO


def credit_account(operation_id: UniqueID, account_id: UniqueID, account_repo: AccountWriteRepository,
                   amount_dto: AmountDTO) -> None:
    amount = Amount(amount_dto.dollars, amount_dto.cents)
    account = account_repo.get_by_id(account_id)
    account.credit(amount, operation_id)
    account_repo.save(account)


def debit_account(operation_id: UniqueID, account_id: UniqueID, account_repo: AccountWriteRepository,
                  amount_dto: AmountDTO) -> None:
    amount = Amount(amount_dto.dollars, amount_dto.cents)
    account = account_repo.get_by_id(account_id)
    account.debit(amount, operation_id)
    account_repo.save(account)


def change_maximum_debt(operation_id: UniqueID, account_id: UniqueID, account_repo: AccountWriteRepository,
                        amount_dto: AmountDTO) -> None:
    amount = Amount(amount_dto.dollars, amount_dto.cents)
    account = account_repo.get_by_id(account_id)
    account.set_maximum_debt(amount, operation_id)
    account_repo.save(account)


def create_account(operation_id: UniqueID, account_name: str, client_id: UniqueID, account_repo: AccountWriteRepository,
                   default_maximum_debt: Optional[AmountDTO] = None) -> Account:
    account = Account.create(client_id, UniqueID(), operation_id, account_name)
    if default_maximum_debt:
        account.set_maximum_debt(Amount(default_maximum_debt.dollars, default_maximum_debt.cents), UniqueID())
    account_repo.save(account)
    return account
