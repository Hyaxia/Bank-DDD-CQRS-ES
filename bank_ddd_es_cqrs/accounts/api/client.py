from flask import Response, request
from flask_restplus import Namespace, Resource  # type: ignore
from bank_ddd_es_cqrs.shared.model import UniqueID, StatusCodes
from ..use_cases import add_account_to_client, create_client, ClientDetailsDTO
from ..composition_root import get_client_write_repo
from .operation_id import get_operation_id
from .validation import client_add_account_parser, client_create_parser
from werkzeug.exceptions import BadRequest
from bank_ddd_es_cqrs.shared.logger import logger
from bank_ddd_es_cqrs.shared.model import AppException

client_ns = Namespace('Client', description='Client related operations')


class ClientAccount(Resource):
    @client_ns.expect(client_add_account_parser)
    @client_ns.doc(
        responses={200: 'Balance change command has been successfully committed',
                   400: 'Bad client data',
                   409: 'Conflict with current state (trying to change stale state)',
                   500: 'Interval Server Error'})
    def post(self, client_id: str) -> (str, int):
        try:
            args = client_add_account_parser.parse_args()
            operation_id = get_operation_id(args)
            new_account_name = args['account_name']
            with get_client_write_repo() as client_repo:
                new_account_id = add_account_to_client(operation_id, UniqueID(client_id), client_repo, new_account_name)
            return Response(
                status=StatusCodes.CREATED.value,
                headers={
                    'Location': request.base_url + f'/{new_account_id}'
                }
            )
        except AppException as e:
            return {'message': str(e)}, e.status
        except BadRequest as e:
            return e.data['errors'], e.code
        except ValueError as e:
            return {'message': str(e)}, StatusCodes.INVALID_USER_DATA.value
        except Exception as e:
            logger.error(e)
            return str(e), StatusCodes.INTERNAL_SERVER_ERROR.value


class Client(Resource):
    @client_ns.expect(client_create_parser)
    @client_ns.doc(
        responses={200: 'Balance change command has been successfully committed',
                   400: 'Bad client data',
                   409: 'Conflict with current state (trying to change stale state)',
                   500: 'Interval Server Error'})
    def post(self) -> (str, int):
        try:
            args = client_create_parser.parse_args()
            operation_id = get_operation_id(args)
            new_client_details = ClientDetailsDTO(
                args['social_security_number'],
                args['first_name'],
                args['last_name'],
                args['birth_date']
            )
            with get_client_write_repo() as client_repo:
                new_client_id = create_client(
                    operation_id,
                    new_client_details,
                    client_repo
                )
            return Response(
                status=StatusCodes.CREATED.value,
                headers={
                    'Location': request.base_url + f'/{new_client_id}'
                }
            )
        except AppException as e:
            return {'message': str(e)}, e.status
        except BadRequest as e:
            return e.data['errors'], e.code
        except ValueError as e:
            return {'message': str(e)}, StatusCodes.INVALID_USER_DATA.value
        except Exception as e:
            logger.error(e)
            return str(e), StatusCodes.INTERNAL_SERVER_ERROR.value


client_ns.add_resource(Client, '/client')
client_ns.add_resource(ClientAccount, '/client/<client_id>/account')
