import pandas as pd
from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, UniqueConstraint

from Base import Base, TinyInteger, get_next_id, PokeApiResource, CSVData

if TYPE_CHECKING:
    from Berries import BerryFlavor
    from Moves import Move
    from Pokemon import PokemonNature
    from TextEntries import ContestName, ContestEffectEffect, ContestEffectFlavorText, SuperContestEffectFlavorText, BerryFlavorName

class ContestType(Base, PokeApiResource):
    __tablename__ = "ContestType"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    berry_flavor: Mapped["BerryFlavor"] = relationship(back_populates="contest_type", cascade="save-update",
                                                       primaryjoin="ContestType.id == foreign(BerryFlavor.contest_type_key)")#,
                                                       #foreign_keys=berry_flavor_key)
    names: Mapped[List["ContestName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="ContestType.id == foreign(ContestName.object_key)")
    
    moves: Mapped[List["Move"]] = relationship(back_populates="contest_type", cascade="save-update",
                                               primaryjoin="ContestType.id == foreign(Move.contest_type_key)")
    
    # Moved these from BerryFlavor
    flavors: Mapped[List["BerryFlavorName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                            primaryjoin="ContestType.id == foreign(BerryFlavorName.object_key)")

    hates_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="hates_flavor", cascade="save-update",
                                                              primaryjoin="ContestType.id == foreign(PokemonNature.hates_flavor_key)")
    likes_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="likes_flavor", cascade="save-update",
                                                              primaryjoin="ContestType.id == foreign(PokemonNature.likes_flavor_key)")
    
    _cache: Dict[int, "ContestType"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "contest_types.csv", "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_ContestType_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["ContestType"]:
        types_ = []
        for id_, type_data in df.iterrows():
            poke_api_id = id_
            name = type_data.identifier
            type_ = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[type_.poke_api_id] = type_
            types_.append(type_)
        return types_
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

class AbstractContestEffect(Base, PokeApiResource):
    __tablename__ = "ContestEffect"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    super_contest: Mapped[bool] = mapped_column(Boolean)
    appeal: Mapped[int] = mapped_column(TinyInteger)

    __mapper_args__ = {
        "polymorphic_on": "super_contest",
        "polymorphic_abstract": True
    }

    __table_args__ = (
        UniqueConstraint("poke_api_id","super_contest",name="ux_ContestEffect_PokeApiId"),
    )

    def __init__(self, appeal: int):
        self.id = get_next_id()
        self.appeal = appeal

class ContestEffect(AbstractContestEffect):
    jam: Mapped[int] = mapped_column(TinyInteger,nullable=True)
    
    effect_entries: Mapped[List["ContestEffectEffect"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="ContestEffect.id == foreign(ContestEffectEffect.object_key)")
    flavor_text_entries: Mapped[List["ContestEffectFlavorText"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="ContestEffect.id == foreign(ContestEffectFlavorText.object_key)")
    __mapper_args__ = {"polymorphic_identity": False}

    _cache: Dict[int, "ContestEffect"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "contest_effects.csv", "relationships": {}})

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["ContestEffect"]:
        effects = []
        for id_, effect_data in df.iterrows():
            poke_api_id = id_
            appeal = effect_data.appeal
            jam = effect_data.jam
            effect = cls(poke_api_id=poke_api_id, appeal=appeal, jam=jam)
            cls._cache[effect.poke_api_id] = effect
            effects.append(effect)
        return effects
    
    def __init__(self, poke_api_id: int, appeal: int, jam: int):
        super().__init__(appeal)
        self.poke_api_id = poke_api_id
        self.jam = jam

    def compare(self, data):
        if self.appeal != data.appeal:
            self.appeal = data.appeal
        if self.jam != data.jam:
            self.jam = data.jam

class SuperContestEffect(AbstractContestEffect):
    moves: Mapped[List["Move"]] = relationship(back_populates="super_contest_effect", cascade="save-update",
                                                      primaryjoin="SuperContestEffect.id == foreign(Move.super_contest_effect_key)")
    
    flavor_text_entries: Mapped[List["SuperContestEffectFlavorText"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="SuperContestEffect.id == foreign(SuperContestEffectFlavorText.object_key)")
    __mapper_args__ = {"polymorphic_identity": True}

    _cache: Dict[int, "SuperContestEffect"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "super_contest_effects.csv", "relationships": {}})

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["SuperContestEffect"]:
        effects = []
        for id_, effect_data in df.iterrows():
            poke_api_id = id_
            appeal = effect_data.appeal
            effect = cls(poke_api_id=poke_api_id, appeal=appeal)
            cls._cache[effect.poke_api_id] = effect
            effects.append(effect)
        return effects
    
    def __init__(self, poke_api_id: int, appeal: int):
        super().__init__(appeal)
        self.poke_api_id = poke_api_id

    def compare(self, data):
        if self.appeal != data.appeal:
            self.appeal = data.appeal

