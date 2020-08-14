from flask import Blueprint
from flask_restplus import Api  # type: ignore
from .account import account_ns
from .client import client_ns


account_blueprint = Blueprint('Banking API', __name__)
account_api = Api(account_blueprint, version='1.0', title='Account API',
                  description='Handling account related actions')

account_api.add_namespace(account_ns, '/api/v1')
account_api.add_namespace(client_ns, '/api/v1')


# TODO: maybe I should change the way I designed the api, maybe it should be hierarchical instead of just separated
#  https://www.moesif.com/blog/technical/api-design/REST-API-Design-Best-Practices-for-Sub-and-Nested-Resources/
