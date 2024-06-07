from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Table, Column, ForeignKey, Boolean, UniqueConstraint

from Base import Base, TinyInteger, EncounterToEncounterCondValLink, get_next_id, PokeApiResource

if TYPE_CHECKING:
    from Pokemon import PokemonEncounter
    from TextEntries import EncounterMethodName, EncounterConditionName, EncounterConditionValueName

class Encounter(Base):
    __tablename__ = "Encounter"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    min_level: Mapped[int] = mapped_column(TinyInteger)
    max_level: Mapped[int] = mapped_column(TinyInteger)
    chance: Mapped[int] = mapped_column(TinyInteger)
    method_key: Mapped[int] = mapped_column(Integer)
    pokemon_encounter_key: Mapped[int] = mapped_column(Integer)

    method: Mapped["EncounterMethod"] = relationship(back_populates="encounters", cascade="save-update",
                                                     primaryjoin="Encounter.method_key == EncounterMethod.id",
                                                     foreign_keys=method_key)
    pokemon_encounter: Mapped["PokemonEncounter"] = relationship(back_populates="encounter_details", cascade="save-update",
                                                                 primaryjoin="Encounter.pokemon_encounter_key == PokemonEncounter.id",
                                                                 foreign_keys=pokemon_encounter_key)
    condition_values: Mapped[List["EncounterConditionValue"]] = relationship(back_populates="encounters", secondary=EncounterToEncounterCondValLink,  cascade="save-update")

    __table_args__ = (
        UniqueConstraint("pokemon_encounter_key","method_key",name="ux_Encounter_pokemon_encounter_method"),
    )

    @classmethod
    def parse_data(cls,data) -> "Encounter":
        min_level = data.min_level
        max_level = data.max_level
        chance = data.chance
        encounter = cls(min_level = min_level, max_level = max_level, chance = chance)
        #cls._cache[evolution_chain.poke_api_id] = evolution_chain
        return encounter
    
    def __init__(self, min_level: int, max_level: int, chance: int):
        self.id = get_next_id()
        self.min_level = min_level
        self.max_level = max_level
        self.chance = chance

    def compare(self, data):
        if self.min_level != data.min_level:
            self.min_level = data.min_level
        if self.max_level != data.max_level:
            self.max_level = data.max_level
        if self.chance != data.chance:
            self.chance = data.chance

class EncounterMethod(Base, PokeApiResource):
    __tablename__ = "EncounterMethod"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(TinyInteger)

    encounters: Mapped[List["Encounter"]] = relationship(back_populates="method", cascade="save-update",
                                                        primaryjoin="EncounterMethod.id == foreign(Encounter.method_key)")

    names: Mapped[List["EncounterMethodName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="EncounterMethod.id == foreign(EncounterMethodName.object_key)")
    
    _cache: Dict[int, "EncounterMethod"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EncounterMethod_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "EncounterMethod":
        poke_api_id = data.id_
        name = data.name
        order = data.order

        method = cls(poke_api_id=poke_api_id, name=name, order=order)
        cls._cache[method.poke_api_id] = method
        return method
    
    def __init__(self, poke_api_id: int, name: str, order: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.order = order

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name
        if self.order != data.order:
            self.order = data.order

class EncounterCondition(Base, PokeApiResource):
    __tablename__ = "EncounterCondition"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    names: Mapped[List["EncounterConditionName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="EncounterCondition.id == foreign(EncounterConditionName.object_key)")
    values: Mapped[List["EncounterConditionValue"]] = relationship(back_populates="condition", cascade="save-update",
                                                                   primaryjoin="EncounterCondition.id == foreign(EncounterConditionValue.condition_key)")
    
    _cache: Dict[int, "EncounterCondition"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EncounterCondition_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "EncounterCondition":
        poke_api_id = data.id_
        name = data.name

        condition = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[condition.poke_api_id] = condition
        return condition
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name

class EncounterConditionValue(Base, PokeApiResource):
    __tablename__ = "EncounterConditionValue"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    condition_key: Mapped[int] = mapped_column(Integer)

    condition: Mapped["EncounterCondition"] = relationship(back_populates="values", cascade="save-update",
                                                           primaryjoin="EncounterConditionValue.condition_key == EncounterCondition.id",
                                                           foreign_keys=condition_key)

    encounters: Mapped[List["Encounter"]] = relationship(back_populates="condition_values", secondary=EncounterToEncounterCondValLink,  cascade="save-update")

    names: Mapped[List["EncounterConditionValueName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="EncounterConditionValue.id == foreign(EncounterConditionValueName.object_key)")
    
    _cache: Dict[int, "EncounterConditionValue"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EncounterConditionValuePokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "EncounterConditionValue":
        poke_api_id = data.id_
        name = data.name

        value = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[value.poke_api_id] = value
        return value
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name