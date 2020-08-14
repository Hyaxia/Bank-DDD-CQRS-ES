from typing import Dict, Any
from bank_ddd_es_cqrs.shared.model import UniqueID


def get_operation_id(args: Dict[Any, Any]) -> UniqueID:
    try:
        operation_id = args['operation_id']
        if operation_id:
            return UniqueID(operation_id)
        else:
            return UniqueID()
    except KeyError:
        return UniqueID()
