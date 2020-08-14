import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from dotenv import load_dotenv

load_dotenv(verbose=True, dotenv_path='/home/max/software/projects/Bank-DDD-CQRS-ES/.env.local.dev')

from bank_ddd_es_cqrs.server import app
from bank_ddd_es_cqrs.accounts.infrastructure import event_store_db

if __name__ == '__main__':
    # with app.app_context():
    #     event_store_db.create_all()
    app.run(debug=True, port=int(os.environ['ACCOUNTS_PORT']))
