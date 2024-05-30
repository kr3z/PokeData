from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, UniqueConstraint

from Base import Base, TinyInteger, get_next_id, PokeApiResource

if TYPE_CHECKING:
    from Berries import BerryFlavor
    from Moves import Move
    from TextEntries import ContestName, ContestEffectEffect, ContestEffectFlavorText, SuperContestEffectFlavorText

class ContestType(Base, PokeApiResource):
    __tablename__ = "ContestType"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    #berry_flavor_key: Mapped[int] = mapped_column(Integer)

    berry_flavor: Mapped["BerryFlavor"] = relationship(back_populates="contest_type", cascade="save-update",
                                                       primaryjoin="ContestType.id == foreign(BerryFlavor.contest_type_key)")#,
                                                       #foreign_keys=berry_flavor_key)
    names: Mapped[List["ContestName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="ContestType.id == foreign(ContestName.object_key)")
    
    moves: Mapped[List["Move"]] = relationship(back_populates="contest_type", cascade="save-update",
                                               primaryjoin="ContestType.id == foreign(Move.contest_type_key)")
    
    _cache: Dict[int, "ContestType"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_ContestType_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "ContestType":
        poke_api_id = data.id_
        name = data.name

        contest = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[contest.poke_api_id] = contest
        return contest
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name

class AbstractContestEffect(Base):
    __tablename__ = "ContestEffect"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    super_contest: Mapped[bool] = mapped_column(Boolean)
    appeal: Mapped[int] = mapped_column(TinyInteger)

    __mapper_args__ = {
        "polymorphic_on": "super_contest",
        "polymorphic_abstract": True
    }

class ContestEffect(AbstractContestEffect):
    jam: Mapped[int] = mapped_column(TinyInteger,nullable=True)
    moves: Mapped[List["Move"]] = relationship(back_populates="contest_effect", cascade="save-update",
                                                      primaryjoin="ContestEffect.id == foreign(Move.contest_effect_key)")
    
    effect_entries: Mapped[List["ContestEffectEffect"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="ContestEffect.id == foreign(ContestEffectEffect.object_key)")
    flavor_text_entries: Mapped[List["ContestEffectFlavorText"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="ContestEffect.id == foreign(ContestEffectFlavorText.object_key)")
    __mapper_args__ = {"polymorphic_identity": False}

class SuperContestEffect(AbstractContestEffect):
    moves: Mapped[List["Move"]] = relationship(back_populates="super_contest_effect", cascade="save-update",
                                                      primaryjoin="SuperContestEffect.id == foreign(Move.super_contest_effect_key)")
    
    flavor_text_entries: Mapped[List["SuperContestEffectFlavorText"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="SuperContestEffect.id == foreign(SuperContestEffectFlavorText.object_key)")
    __mapper_args__ = {"polymorphic_identity": True}

class AbstractContestChain(Base):
    __tablename__ = "ContestChain"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    super_contest: Mapped[bool] = mapped_column(Boolean)

    __mapper_args__ = {
        "polymorphic_on": "super_contest",
        "polymorphic_abstract": True
    }

class ContestChain(AbstractContestChain):
    move_key: Mapped[int] = mapped_column(Integer)
    use_after_key: Mapped[Optional[int]] = mapped_column(Integer)

    move: Mapped["Move"] = relationship(back_populates="contest_combos", cascade="save-update",
                                        primaryjoin="Move.id == ContestChain.move_key",
                                        foreign_keys=move_key)
    
    use_after: Mapped["ContestChain"] = relationship(back_populates="use_before", remote_side="ContestChain.id",
                                                     primaryjoin="ContestChain.use_after_key == ContestChain.id",
                                                     foreign_keys=use_after_key)
    
    use_before: Mapped[List["ContestChain"]] = relationship(back_populates="use_after",
                                                      primaryjoin="ContestChain.id == foreign(ContestChain.use_after_key)")
    
    __mapper_args__ = {"polymorphic_identity": False}

class SuperContestChain(AbstractContestChain):
    move_key: Mapped[int] = mapped_column(Integer, use_existing_column=True)
    use_after_key: Mapped[Optional[int]] = mapped_column(Integer, use_existing_column=True)

    move: Mapped["Move"] = relationship(back_populates="super_contest_combos", cascade="save-update",
                                        primaryjoin="Move.id == SuperContestChain.move_key",
                                        foreign_keys=move_key)
    
    use_after: Mapped["SuperContestChain"] = relationship(back_populates="use_before", remote_side="SuperContestChain.id",
                                                     primaryjoin="SuperContestChain.use_after_key == SuperContestChain.id",
                                                     foreign_keys=use_after_key)
    
    use_before: Mapped[List["SuperContestChain"]] = relationship(back_populates="use_after",
                                                      primaryjoin="SuperContestChain.id == foreign(SuperContestChain.use_after_key)")
    
    __mapper_args__ = {"polymorphic_identity": True}

