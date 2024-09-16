import pandas as pd
from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, UniqueConstraint

from Base import Base, TinyInteger, EncounterToEncounterCondValLink, get_next_id, PokeApiResource, CSVData, CSVResource, ManyToOneAttrs, ManyToManyAttr, MergeCSV, GroupByCSV

if TYPE_CHECKING:
    from Games import VersionGroup, Version
    from Locations import LocationArea
    from Pokemon import Pokemon
    from TextEntries import EncounterMethodName, EncounterConditionName, EncounterConditionValueName

class Encounter(Base, PokeApiResource):
    __tablename__ = "Encounter"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    min_level: Mapped[int] = mapped_column(TinyInteger)
    max_level: Mapped[int] = mapped_column(TinyInteger)
    version_key: Mapped[int] = mapped_column(Integer)
    location_area_key: Mapped[int] = mapped_column(Integer)
    encounter_slot_key: Mapped[int] = mapped_column(Integer)
    pokemon_key: Mapped[int] = mapped_column(Integer)

    version: Mapped["Version"] = relationship(cascade="save-update",
                                              primaryjoin="Encounter.version_key == Version.id",
                                              foreign_keys=version_key)
    location_area: Mapped["LocationArea"] = relationship(back_populates="encounters", cascade="save-update",
                                                         primaryjoin="Encounter.location_area_key == LocationArea.id",
                                                         foreign_keys=location_area_key)
    encounter_slot: Mapped["EncounterSlot"] = relationship(cascade="save-update",
                                                           primaryjoin="Encounter.encounter_slot_key == EncounterSlot.id",
                                                           foreign_keys=encounter_slot_key)
    pokemon: Mapped["Pokemon"] = relationship(back_populates="encounters", cascade="save-update",
                                              primaryjoin="Encounter.pokemon_key == Pokemon.id",
                                              foreign_keys=pokemon_key)

    condition_values: Mapped[List["EncounterConditionValue"]] = relationship(back_populates="encounters", secondary=EncounterToEncounterCondValLink,  cascade="save-update")

    _cache: Dict[int, "Encounter"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "encounters.csv",
                                   "merge_csvs": (MergeCSV("encounter_condition_value_map.csv", "encounter_id"),),
                                   "group_by": GroupByCSV(['encounter_condition_value_id'], ['id','version_id','location_area_id','encounter_slot_id','pokemon_id','min_level','max_level']),
                          "relationships": {"version_id": ManyToOneAttrs("version","version_key"),
                                            "location_area_id": ManyToOneAttrs("location_area","location_area_key"),
                                            "encounter_slot_id": ManyToOneAttrs("encounter_slot","encounter_slot_key"),
                                            "pokemon_id": ManyToOneAttrs("pokemon","pokemon_key"),
                                            "encounter_condition_value_id": ManyToManyAttr("condition_values")}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Encounter_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["Encounter"]:
        encounters = []
        for id_, slot_data in df.iterrows():
            poke_api_id = id_
            min_level = slot_data.min_level
            max_level = slot_data.max_level
            encounter = cls(poke_api_id=poke_api_id, min_level=min_level, max_level=max_level)
            cls._cache[encounter.poke_api_id] = encounter
            encounters.append(encounter)
        return encounters
    
    def __init__(self, poke_api_id: int, min_level: int, max_level: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.min_level = min_level
        self.max_level = max_level

    def compare(self, data):
        if self.min_level != data.min_level:
            self.min_level = data.min_level
        if self.max_level != data.max_level:
            self.max_level = data.max_level

class EncounterSlot(Base,PokeApiResource):
    __tablename__ = "EncounterSlot"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    slot: Mapped[Optional[int]] = mapped_column(TinyInteger)
    rarity: Mapped[int] = mapped_column(TinyInteger)
    version_group_key: Mapped[int] = mapped_column(Integer)
    encounter_method_key: Mapped[int] = mapped_column(Integer)

    version_group: Mapped["VersionGroup"] = relationship(cascade="save-update",
                                                         primaryjoin="EncounterSlot.version_group_key == VersionGroup.id",
                                                         foreign_keys=version_group_key)
    encounter_method: Mapped["EncounterMethod"] = relationship(cascade="save-update",
                                                               primaryjoin="EncounterSlot.encounter_method_key == EncounterMethod.id",
                                                               foreign_keys=encounter_method_key)

    _cache: Dict[int, "EncounterSlot"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "encounter_slots.csv",
                          "relationships": {"version_group_id": ManyToOneAttrs("version_group","version_group_key"),
                                            "encounter_method_id": ManyToOneAttrs("encounter_method","encounter_method_key")}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EncounterSlot_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["EncounterSlot"]:
        encounter_slots = []
        for id_, slot_data in df.iterrows():
            poke_api_id = id_
            slot = slot_data.slot
            rarity = slot_data.rarity
            encounter_slot = cls(poke_api_id=poke_api_id, slot=slot, rarity=rarity)
            cls._cache[encounter_slot.poke_api_id] = encounter_slot
            encounter_slots.append(encounter_slot)
        return encounter_slots
    
    def __init__(self, poke_api_id: int, slot: int, rarity: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.slot = slot
        self.rarity = rarity

    def compare(self, data):
        if self.slot != data.slot:
            self.slot = data.slot
        if self.rarity != data.rarity:
            self.rarity = data.rarity

class EncounterMethod(Base, PokeApiResource):
    __tablename__ = "EncounterMethod"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(TinyInteger)

    names: Mapped[List["EncounterMethodName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="EncounterMethod.id == foreign(EncounterMethodName.object_key)")
    
    _cache: Dict[int, "EncounterMethod"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "encounter_methods.csv",
                          "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EncounterMethod_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["EncounterMethod"]:
        methods = []
        for id_, method_data in df.iterrows():
            poke_api_id = id_
            name = method_data.identifier
            order = method_data.order
            method = cls(poke_api_id=poke_api_id, name=name, order=order)
            cls._cache[method.poke_api_id] = method
            methods.append(method)
        return methods
    
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
    csv_data: CSVData = CSVData(**{"primary_csv": "encounter_conditions.csv",
                          "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EncounterCondition_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["EncounterCondition"]:
        conditions = []
        for id_, condition_data in df.iterrows():
            poke_api_id = id_
            name = condition_data.identifier
            condition = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[condition.poke_api_id] = condition
            conditions.append(condition)
        return conditions
    
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
    is_default: Mapped[bool] = mapped_column(Boolean)
    condition_key: Mapped[int] = mapped_column(Integer)

    condition: Mapped["EncounterCondition"] = relationship(back_populates="values", cascade="save-update",
                                                           primaryjoin="EncounterConditionValue.condition_key == EncounterCondition.id",
                                                           foreign_keys=condition_key)

    encounters: Mapped[List["Encounter"]] = relationship(back_populates="condition_values", secondary=EncounterToEncounterCondValLink,  cascade="save-update")

    names: Mapped[List["EncounterConditionValueName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="EncounterConditionValue.id == foreign(EncounterConditionValueName.object_key)")
    
    _cache: Dict[int, "EncounterConditionValue"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "encounter_condition_values.csv",
                          "relationships": {"encounter_condition_id": ManyToOneAttrs("condition","condition_key")}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EncounterConditionValuePokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["EncounterConditionValue"]:
        values = []
        for id_, value_data in df.iterrows():
            poke_api_id = id_
            name = value_data.identifier
            is_default = value_data.is_default
            value = cls(poke_api_id=poke_api_id, name=name, is_default=is_default)
            cls._cache[value.poke_api_id] = value
            values.append(value)
        return values
    
    def __init__(self, poke_api_id: int, name: str, is_default: bool):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.is_default = is_default

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name
        if self.is_default != data.is_default:
            self.is_default = data.is_default