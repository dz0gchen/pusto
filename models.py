import csv
import uuid

from datetime import date
from enum import Enum
from typing import Any

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.sqlite import BOOLEAN, DATE, INTEGER, VARCHAR
from sqlalchemy.orm import declarative_base, relationship, validates, Session

Base: Any = declarative_base()


class Scores(Enum):
    MID = 100


class Player(Base):
    __tablename__ = "players"

    player_id = Column(
        VARCHAR(36),
        nullable=False,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
    )
    name = Column(VARCHAR(100), nullable=False, unique=True)
    levels = relationship("PlayerLevel", backref="players", cascade="all, delete")


class Level(Base):
    __tablename__ = "levels"

    level_id = Column(INTEGER, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(100), nullable=False, unique=True)
    levels = relationship("PlayerLevel", backref="levels", cascade="all, delete")
    prizes = relationship("LevelPrize", backref="levels", cascade="all, delete")


class Prize(Base):
    __tablename__ = "prizes"

    prize_id = Column(INTEGER, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(100), unique=True)
    prizes = relationship("LevelPrize", backref="prizes", cascade="all, delete")


class PlayerLevel(Base):
    __tablename__ = "player_levels"

    player = Column(VARCHAR(36), ForeignKey(Player.player_id), primary_key=True)
    level = Column(INTEGER, ForeignKey(Level.level_id), primary_key=True)
    completed = Column(DATE)
    is_completed = Column(BOOLEAN, default=False)
    score = Column(INTEGER, default=0)

    @validates("score")
    def validate_score(self, _, value):
        if value < 0:
            raise ValueError("the field cannot have a negative value")
        return value

    @classmethod
    # метод вызывается после прохождения уровня игроком
    def completed_level(
        cls, session: Session, player: Column[str], level: Column[int]
    ) -> bool:
        player_level = (
            session.query(PlayerLevel).filter_by(player=player, level=level).one()
        )
        if player_level.is_completed:
            return False
        player_level.is_completed = True
        player_level.completed = date.today()
        session.commit()
        # отдаем подарок когда набраны очки  ¯\_(ツ)_/¯
        if player_level.score > Scores.MID.value:
            # вывод в консоль для наглядности, some internal event ...
            print(LevelPrize.received_gift(session, player=player, level=level))
        return True

    @classmethod
    def export_to_csv(cls, session: Session, offset: int = 100):
        # итерируемся по всей таблице, делать индексы для конкретных полей в этой задаче не будем
        # алхимия не возвращает генераторы, кастомим пагинацию
        with open("output.csv", "w") as f:
            writer = csv.writer(f)
            page_number = 0
            while True:
                # на объеме данных > 50000 запрос query(PlayerLevel).join(Level) работает значительно медленее, откажемся от join ...
                # когда не важен порядок вставки в cvs можно получать данные через offset в тредах ...
                q = (
                    session.query(PlayerLevel, Level, LevelPrize, Prize)
                    .filter(PlayerLevel.level == Level.level_id)
                    .filter(Level.level_id == LevelPrize.level)
                    .filter(LevelPrize.prize == Prize.prize_id)
                    .limit(offset)
                    .offset(offset * page_number)
                    .all()
                )
                if not q:
                    break
                # запрос уходит в базу только после итерации по объекту запроса
                for pl, l, _, p in q:
                    writer.writerow(
                        (pl.player, l.title, pl.is_completed, pl.score, p.title),
                    )
                page_number += 1


class LevelPrize(Base):
    __tablename__ = "level_prizes"

    level = Column(INTEGER, ForeignKey(Level.level_id), primary_key=True)
    prize = Column(INTEGER, ForeignKey(Prize.prize_id), primary_key=True)
    received = Column(DATE)

    @classmethod
    def received_gift(
        cls, session: Session, player: Column[str], level: Column[int]
    ) -> tuple[Column[str], Column[str]]:
        level_prize = session.query(LevelPrize).filter_by(level=level).one()
        level_prize.received = date.today()
        session.commit()
        prize = session.get(Prize, level_prize.prize)
        return (player, prize.title)
