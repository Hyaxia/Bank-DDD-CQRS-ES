from flask_restplus import reqparse  # type: ignore


account_balance_parser = reqparse.RequestParser()
account_balance_parser.add_argument('action',
                                    type=str,
                                    choices=('credit', 'debit'),
                                    help='Name of the action we want to perform',
                                    required=True)
account_balance_parser.add_argument('dollars',
                                    type=int,
                                    help='dollars to credit or debit',
                                    required=True)
account_balance_parser.add_argument('cents',
                                    type=int,
                                    help='cents to credit or debit',
                                    required=True)
account_balance_parser.add_argument('operation_id',
                                    type=str,
                                    help='operation id that will be used to perform the task, '
                                         'if not specified will be generated')

client_add_account_parser = reqparse.RequestParser()
client_add_account_parser.add_argument('operation_id',
                                       type=str,
                                       help='operation id that will be used to perform the task, '
                                            'if not specified will be generated')
client_add_account_parser.add_argument('account_name',
                                       type=str,
                                       required=True,
                                       help='Name of the account to create')

client_create_parser = reqparse.RequestParser()
client_create_parser.add_argument('first_name',
                                  type=str,
                                  required=True,
                                  help='First name of the client')
client_create_parser.add_argument('last_name',
                                  type=str,
                                  required=True,
                                  help='Last name of the client')
client_create_parser.add_argument('birth_date',
                                  type=str,
                                  required=True,
                                  help='Birth date of the client, format - day/month/year - example: 27/02/1998')
client_create_parser.add_argument('social_security_number',
                                  type=int,
                                  required=True,
                                  help='Social security number of the client - 9 digit number')
