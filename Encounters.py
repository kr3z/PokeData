from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Table, Column, ForeignKey, Boolean

from Base import Base, TinyInteger, EncounterToEncounterCondValLink

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

    method: Mapped["EncounterMethod"] = relationship(back_populates="encounters",
                                                     primaryjoin="Encounter.method_key == EncounterMethod.id",
                                                     foreign_keys=method_key)
    pokemon_encounter: Mapped["PokemonEncounter"] = relationship(back_populates="encounter_details",
                                                                 primaryjoin="Encounter.pokemon_encounter_key == PokemonEncounter.id",
                                                                 foreign_keys=pokemon_encounter_key)
    condition_values: Mapped[List["EncounterConditionValue"]] = relationship(back_populates="encounters", secondary=EncounterToEncounterCondValLink)

class EncounterMethod(Base):
    __tablename__ = "EncounterMethod"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(TinyInteger)

    encounters: Mapped[List["Encounter"]] = relationship(back_populates="method",
                                                        primaryjoin="EncounterMethod.id == foreign(Encounter.method_key)")

    names: Mapped[List["EncounterMethodName"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="EncounterMethod.id == foreign(EncounterMethodName.object_key)")

class EncounterCondition(Base):
    __tablename__ = "EncounterCondition"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    names: Mapped[List["EncounterConditionName"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="EncounterCondition.id == foreign(EncounterConditionName.object_key)")
    values: Mapped[List["EncounterConditionValue"]] = relationship(back_populates="condition",
                                                                   primaryjoin="EncounterCondition.id == foreign(EncounterConditionValue.condition_key)")

class EncounterConditionValue(Base):
    __tablename__ = "EncounterConditionValue"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    condition_key: Mapped[int] = mapped_column(Integer)

    condition: Mapped["EncounterCondition"] = relationship(back_populates="values",
                                                           primaryjoin="EncounterConditionValue.condition_key == EncounterCondition.id",
                                                           foreign_keys=condition_key)

    encounters: Mapped[List["Encounter"]] = relationship(back_populates="condition_values", secondary=EncounterToEncounterCondValLink)

    names: Mapped[List["EncounterConditionValueName"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="EncounterConditionValue.id == foreign(EncounterConditionValueName.object_key)")