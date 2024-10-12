import pytest
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from boost_models import Base


@pytest.fixture(autouse=True, scope="function")
def setup_database() -> Generator[Engine, None, None]:
    engine = create_engine("sqlite:///pusto_ne_gusto_tests.sqlite")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True, scope="function")
def setup_session(setup_database) -> Generator[Session, None, None]:
    Session = sessionmaker(bind=setup_database)
    session = Session()
    yield session
    session.close()
