import enum
import uuid
from datetime import date
from typing import Any

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.dialects.sqlite import DATE, INTEGER, VARCHAR
from sqlalchemy.orm import declarative_base, relationship, validates, Session


Base: Any = declarative_base()


class BoostTypes(enum.Enum):
    free = "free"
    premium = "premium"


class PlayerB(Base):
    __tablename__ = "players_b"

    player_id = Column(
        VARCHAR(36),
        nullable=False,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
    )
    name = Column(VARCHAR(100), nullable=False, unique=True)
    last_login = Column(DATE, nullable=True)
    boosts = relationship("PlayerBoost", backref="players_b", cascade="all, delete")

    @validates("last_login")
    def validate_last_login(self, _, value):
        # отправляем событие, первый вход
        if self.last_login is None and isinstance(value, date):
            raise Exception("Send login event to analytic endpoint or databus")

    @classmethod
    def increase_boosts(
        cls, session: Session, player: Column[str], boosts: list[str]
    ) -> None:
        player = session.get(PlayerB, player)
        _boosts = session.query(Boost).filter(Boost.title.in_(boosts)).all()
        for boost in _boosts:
            player.boosts.append(PlayerBoost(boost=boost.boost_id))
        session.commit()


class Boost(Base):
    __tablename__ = "boosts"

    boost_id = Column(INTEGER, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(100), unique=True)
    type = Column(Enum(BoostTypes), nullable=False, default=BoostTypes.free)


class PlayerBoost(Base):
    __tablename__ = "player_boosts"

    player = Column(INTEGER, ForeignKey(PlayerB.player_id), primary_key=True)
    boost = Column(INTEGER, ForeignKey(Boost.boost_id), primary_key=True)
