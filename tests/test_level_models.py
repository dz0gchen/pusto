import pytest

from datetime import date
from typing import Generator
from sqlalchemy.orm import Session

from level_models import PlayerL, PlayerLevel, Prize, Level, LevelPrize


@pytest.fixture(scope="function")
def setup_data(setup_session) -> Generator[Session, None, None]:
    session = setup_session

    prize1 = Prize(title="Greetings")
    prize2 = Prize(title="Bubble gum")
    prize3 = Prize(title="Сandy")

    level1 = Level(title="Level 1")
    level2 = Level(title="Level 2")
    level3 = Level(title="Level 3")

    player1 = PlayerL(name="Player 1")
    player2 = PlayerL(name="Player 2")
    player3 = PlayerL(name="Player 3")

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


def test_relations_in_models(setup_data):
    session = setup_data

    results = session.query(PlayerLevel).all()
    assert len(results) == 3
    results = session.query(PlayerL).filter_by(name="Player 1").one()
    session.delete(results)
    results = session.query(Level).filter_by(title="Level 2").one()
    session.delete(results)
    results = session.query(Prize).filter_by(title="Greetings").one()
    session.delete(results)
    session.commit()

    results = session.query(PlayerLevel).all()
    assert len(results) == 1

    results = session.query(LevelPrize).all()
    assert len(results) == 1


def test_completed_level(setup_data):
    session = setup_data

    player = session.query(PlayerL).filter_by(name="Player 1").one()
    assert PlayerLevel.completed_level(session, player=player.player_id, level=1)

    player_level = (
        session.query(PlayerLevel).filter_by(player=player.player_id, level=1).one()
    )
    assert player_level.is_completed
    assert player_level.completed == date.today()


def test_received_gift(setup_data):
    session = setup_data

    player = session.query(PlayerL).filter_by(name="Player 1").one()
    prize = session.query(Prize).filter_by(title="Greetings").one()

    player_id, title_prize = LevelPrize.received_gift(
        session, player=player.player_id, level=1
    )
    assert player_id == player.player_id
    assert title_prize == prize.title

    level_prize = session.query(LevelPrize).filter_by(level=1).one()
    assert level_prize.received == date.today()


def test_export_to_csv(setup_data):
    session = setup_data

    PlayerLevel.export_to_csv(session)
    count = session.query(PlayerLevel).count()

    with open("output.csv", "r") as f:
        lines = f.readlines()
        assert len(lines) == count
