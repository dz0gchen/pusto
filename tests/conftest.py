import pytest
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from models import Base, Player, PlayerLevel, Prize, Level, LevelPrize


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


@pytest.fixture(autouse=True, scope="function")
def setup_data(setup_session) -> Generator[Session, None, None]:

    session = setup_session

    prize1 = Prize(title="Greetings")
    prize2 = Prize(title="Bubble gum")
    prize3 = Prize(title="Сandy")

    level1 = Level(title="Level 1")
    level2 = Level(title="Level 2")
    level3 = Level(title="Level 3")

    player1 = Player(name="Player 1")
    player2 = Player(name="Player 2")
    player3 = Player(name="Player 3")

    session.add_all(
        (prize1, prize2, prize3, level1, level2, level3, player1, player2, player3)
    )
    session.commit()

    player1.levels.append(PlayerLevel(level=level1.level_id, score=200))
    player2.levels.append(PlayerLevel(level=level2.level_id, score=100))
    player3.levels.append(PlayerLevel(level=level3.level_id, score=50))

    prize1.prizes.append(LevelPrize(level=level1.level_id))
    prize2.prizes.append(LevelPrize(level=level2.level_id))
    prize3.prizes.append(LevelPrize(level=level3.level_id))

    session.commit()

    yield session
