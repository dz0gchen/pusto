import pytest
from datetime import date
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from boost_models import Base, Boost, BoostTypes, Player, PlayerBoost


@pytest.fixture(autouse=True, scope="function")
def setup_database() -> Generator[Engine, None, None]:
    engine = create_engine("sqlite:///pusto_ne_gusto_tests_boosts.sqlite")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True, scope="function")
def setup_session(setup_database) -> Generator[Session, None, None]:
    Session = sessionmaker(bind=setup_database)
    session = Session()
    yield session
    session.close()


@pytest.fixture(autouse=True, scope="function")
def setup_data(setup_session) -> Generator[Session, None, None]:

    session = setup_session

    boost1 = Boost(title="After completed")
    boost2 = Boost(title="Premium", type=BoostTypes.premium)

    player1 = Player(name="Player 1")

    session.add_all((boost1, boost2, player1))
    session.commit()
    yield session


def test_player_model(setup_data):
    session = setup_data

    player = session.query(Player).filter_by(name="Player 1").one()
    with pytest.raises(Exception) as exc_info:
        player.last_login = date.today()
        session.commit()
        assert str(exc_info.value) == "Send login event to analytic endpoin or databus"


def test_increase_boosts(setup_data):
    session = setup_data

    player = session.query(Player).filter_by(name="Player 1").one()
    player_id = player.player_id
    boosts = ["After completed", "Premium"]
    Player.increase_boosts(session, player_id, boosts)
    count = session.query(PlayerBoost).count()
    assert len(boosts) == count
