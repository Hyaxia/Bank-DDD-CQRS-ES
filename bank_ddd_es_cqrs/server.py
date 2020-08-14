"""Main module."""
"""
Resources:
 - Simple CQRS, great project to learn from - https://github.com/gregoryyoung/m-r
 - DDD forum project for my project structure - https://github.com/stemmlerjs/ddd-forum
 - Great examples in python of how to implement certain concepts in ES - https://breadcrumbscollector.tech/implementing-event-sourcing-in-python-part-2-robust-event-store-atop-postgresql/

 From the articles above we get the general sense of how the CQRS and ES work together.
 I have decided to use the optimistic locking technique, as shown in the articles above, and to add a version to the
 aggregate root, and this way to ensure we dont have concurrency problems.

 - To ensure idempotency we use the advices from the following article - https://blog.sapiensworks.com/post/2015/08/26/How-To-Ensure-Idempotency
   The need for idempotency is explained in the article, but basically, if some part of the system shuts down,
   we want to replay the needed commands only once, else, we will perform actions that the user did not intended to.
   We are making sure that the aggregate root knows what operation_id's were called on it, and this way provide idempotency
   In the read model, as the article advice, we will use an idempotency_id which is a combination of the operation_id and some other unique id
"""
import os
from bank_ddd_es_cqrs.accounts.app import account_app_factory

DB_STRING = f"postgres://{os.environ['ACCOUNTS_DB_USER']}:{os.environ['ACCOUNTS_DB_PASSWORD']}@{os.environ['ACCOUNTS_DB_HOST']}:" \
    f"{os.environ['ACCOUNTS_DB_PORT']}/{os.environ['ACCOUNTS_DB_NAME']}"

app = account_app_factory(DB_STRING)
