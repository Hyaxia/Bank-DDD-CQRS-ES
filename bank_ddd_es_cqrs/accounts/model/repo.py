from ..model import Account, Client
from ...shared.model.repo import WriteRepository


class AccountWriteRepository(WriteRepository[Account]):
    pass


class ClientWriteRepository(WriteRepository[Client]):
    pass

