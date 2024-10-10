from datetime import date
from models import Player, PlayerLevel, Prize, Level, LevelPrize


def test_relations_in_models(setup_data):
    session = setup_data

    results = session.query(PlayerLevel).all()
    assert len(results) == 3
    results = session.query(Player).filter_by(name="Player 1").one()
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

    player = session.query(Player).filter_by(name="Player 1").one()
    assert PlayerLevel.completed_level(session, player=player.player_id, level=1)

    player_level = (
        session.query(PlayerLevel).filter_by(player=player.player_id, level=1).one()
    )
    assert player_level.is_completed
    assert player_level.completed == date.today()


def test_received_gift(setup_data):
    session = setup_data

    player = session.query(Player).filter_by(name="Player 1").one()
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

    count = session.query(PlayerLevel).count()
    PlayerLevel.export_to_csv(session)

    with open("output.csv", "r") as f:
        lines = f.readlines()
        assert len(lines) == count
