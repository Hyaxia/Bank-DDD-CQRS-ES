Bank DDD ES CQRS - WIP
================

An example project of using ES + CQRS while using the DDD approach and clean architecture


* Free software: MIT license

Resources and explanations for different motives
--------
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

How To Run?
----------
Docker is required to run this project.

- Clone the project and enter the cloned directory
- Run `docker-compose build`
- Run `docker-compose up -d`
- Wait for kafka-connect to finish initialization (you can check it by `docker-compose ps` and see its status, its supposeto be `healthy`)
- Perform a REST request to the kafka connect instance we have to create the debezium connector that will query the events table:
    - url to post the request to is the url of the kafka connect rest api - `http://localhost:8083/connectors`
    - data is as follows:

```
{
    "name": "postgres-accounts",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "database.hostname": "db",
        "database.port": "5432",
        "database.user": "postgres",
        "database.password": "123456789",
        "database.dbname": "postgres",
        "database.server.name": "accounts",
        "table.whitelist": "public.events",
        "tasks.max": "1",
        "plugin.name": "pgoutput",
        "database.history.kafka.bootstrap.servers": "kafka-1:19092,kafka-2:29092,kafka-3:39092",
        "database.history.kafka.topic": "schema-changes.accounts"
    }
}
```


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
