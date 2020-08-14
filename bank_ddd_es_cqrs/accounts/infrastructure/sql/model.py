from typing import Any, Iterator
from contextlib import contextmanager
from sqlalchemy import Column, Integer, ForeignKey, VARCHAR, JSON  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore


db: Any = SQLAlchemy()


class AggregateModel(db.Model):
    __tablename__ = 'aggregates'

    uuid = Column(VARCHAR(36), primary_key=True)
    version = Column(Integer, default=1)


class EventModel(db.Model):
    __tablename__ = 'events'

    uuid = Column(VARCHAR(36), primary_key=True)
    aggregate_uuid = Column(VARCHAR(36), ForeignKey('aggregates.uuid'))
    name = Column(VARCHAR(50))
    data = Column(JSON)

    aggregate = relationship(AggregateModel, uselist=False, backref='events')


@contextmanager
def session_scope() -> Iterator[Any]:
    """Provide a transactional scope around a series of operations."""
    session = db.session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
