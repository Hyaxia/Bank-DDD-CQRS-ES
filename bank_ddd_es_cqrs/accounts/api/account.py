from flask_restplus import Namespace, Resource  # type: ignore
from ..use_cases import AmountDTO
from .operation_id import get_operation_id
from .validation import account_balance_parser
from ..use_cases import credit_account, debit_account
from ..composition_root import get_account_write_repo
from werkzeug.exceptions import BadRequest
from bank_ddd_es_cqrs.shared.logger import logger
from bank_ddd_es_cqrs.shared.model import AppException, StatusCodes, UniqueID

account_ns = Namespace('Account', description='Account related operations')


class AccountBalance(Resource):
    @account_ns.expect(account_balance_parser)
    @account_ns.doc(
        responses={200: 'Balance change command has been successfully committed',
                   400: 'Bad client data',
                   409: 'Conflict with current state (trying to change stale state)',
                   500: 'Interval Server Error'})
    def patch(self, account_id):
        """
        Change account balance, credit or debit the account
        """
        try:
            args = account_balance_parser.parse_args()
            operation_id = get_operation_id(args)
            action = args['action']
            amount = AmountDTO(
                dollars=args['dollars'],
                cents=args['cents']
            )
            with get_account_write_repo() as account_repo:
                action_func = self._get_func_by_action(action)
                action_func(operation_id, UniqueID(account_id), account_repo, amount)
        except AppException as e:
            return {'message': str(e)}, e.status
        except BadRequest as e:
            return e.data['errors'], e.code
        except ValueError as e:
            return {'message': str(e)}, StatusCodes.INVALID_REQUEST.value
        except Exception as e:
            logger.error(e)
            return str(e), StatusCodes.INTERNAL_SERVER_ERROR.value

    def _get_func_by_action(self, action) -> credit_account or debit_account:
        return {
            'credit': credit_account,
            'debit': debit_account
        }[action]


account_ns.add_resource(AccountBalance, '/account/<account_id>/balance')
