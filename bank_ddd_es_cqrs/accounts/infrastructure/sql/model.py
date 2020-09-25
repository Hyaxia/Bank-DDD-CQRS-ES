import os
from contextlib import contextmanager
from typing import Any, Iterator

from flask_sqlalchemy import SQLAlchemy  # type: ignore
from sqlalchemy import MetaData, Column, Integer, ForeignKey, VARCHAR, JSON, create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship  # type: ignore

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class AggregateModel(Base):
    __tablename__ = 'aggregates'

    uuid = Column(VARCHAR(36), primary_key=True)
    version = Column(Integer, default=1)


class EventModel(Base):
    __tablename__ = 'events'

    uuid = Column(VARCHAR(36), primary_key=True)
    aggregate_uuid = Column(VARCHAR(36), ForeignKey('aggregates.uuid'))
    name = Column(VARCHAR(50))
    data = Column(JSON)

    aggregate = relationship(AggregateModel, uselist=False, backref='events')


db: Any = SQLAlchemy(metadata=metadata)


@contextmanager
def session_scope() -> Iterator[Any]:
    """
    Provide a transactional scope around a series of operations.
    If inside a context of flask app, will return the session from the `db`, otherwise will create a new session.
    """
    try:
        session = db.session()
    except Exception:
        engine = create_engine(
            f"postgres://{os.environ['ACCOUNTS_DB_USER']}:{os.environ['ACCOUNTS_DB_PASSWORD']}@{os.environ['ACCOUNTS_DB_HOST']}:" \
            f"{os.environ['ACCOUNTS_DB_PORT']}/{os.environ['ACCOUNTS_DB_NAME']}"
        )
        session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
