import pandas as pd
from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Table, Column, ForeignKey, Boolean, UniqueConstraint

from Base import Base, TinyInteger, get_next_id, PokeApiResource, CSVData, CSVResource, ManyToOneAttrs

if TYPE_CHECKING:
    from Contests import ContestType
    from Items import Item
    from Pokemon import PokemonType, PokemonNature
    from TextEntries import BerryFirmnessName, BerryFlavorName

class Berry(Base, PokeApiResource):
    __tablename__ = "Berry"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    growth_time: Mapped[int] = mapped_column(TinyInteger)
    max_harvest: Mapped[int] = mapped_column(TinyInteger)
    natural_gift_power: Mapped[int] = mapped_column(TinyInteger)
    size: Mapped[int] = mapped_column(SmallInteger)
    smoothness: Mapped[int] = mapped_column(TinyInteger)
    soil_dryness: Mapped[int] = mapped_column(TinyInteger)
    firmness_key: Mapped[int] = mapped_column(Integer)
    item_key: Mapped[int] = mapped_column(Integer)
    natural_gift_type_key: Mapped[int] = mapped_column(Integer)

    firmness: Mapped["BerryFirmness"] = relationship(back_populates="berries", cascade="save-update",
                                                     primaryjoin="Berry.firmness_key == BerryFirmness.id",
                                                     foreign_keys=firmness_key)
    item: Mapped["Item"] = relationship(back_populates="berry", cascade="save-update",
                                        primaryjoin="Berry.item_key == Item.id",
                                        foreign_keys=item_key)
    natural_gift_type: Mapped["PokemonType"] = relationship(primaryjoin="Berry.natural_gift_type_key == PokemonType.id",
                                                            foreign_keys=natural_gift_type_key, cascade="save-update",)
    
    flavor_map: Mapped[List["BerryFlavor"]] = relationship(back_populates="berry", cascade="save-update",
                                                           primaryjoin="Berry.id == foreign(BerryFlavor.berry_key)")
    
    _cache: Dict[int, "Berry"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "berries.csv", 
                                   "relationships": {"item_id": ManyToOneAttrs("item","item_key"),
                                                     "firmness_id": ManyToOneAttrs("firmness","firmness_key"),
                                                     "natural_gift_type_id": ManyToOneAttrs("natural_gift_type","natural_gift_type_key")}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Berry_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["Berry"]:
        berries = []
        for id_, berry_data in df.iterrows():
            poke_api_id = id_
            growth_time = berry_data.growth_time
            max_harvest = berry_data.max_harvest
            natural_gift_power = berry_data.natural_gift_power
            size = berry_data.size
            smoothness = berry_data.smoothness
            soil_dryness = berry_data.soil_dryness
            berry = cls(poke_api_id=poke_api_id, growth_time=growth_time, max_harvest=max_harvest, 
                    natural_gift_power=natural_gift_power, size=size, smoothness=smoothness, soil_dryness=soil_dryness)
            cls._cache[berry.poke_api_id] = berry
            berries.append(berry)
        return berries
    
    def __init__(self, poke_api_id: int, growth_time: int, max_harvest: int, 
                    natural_gift_power: int, size: int, smoothness: int, soil_dryness: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.growth_time = growth_time
        self.max_harvest = max_harvest
        self.natural_gift_power = natural_gift_power
        self.size = size
        self.smoothness = smoothness
        self.soil_dryness = soil_dryness

    def compare(self, data):
        if self.growth_time != data.growth_time:
            self.growth_time = data.growth_time
        if self.max_harvest != data.max_harvest:
            self.max_harvest = data.max_harvest
        if self.natural_gift_power != data.natural_gift_power:
            self.natural_gift_power = data.natural_gift_power
        if self.size != data.size:
            self.size = data.size
        if self.smoothness != data.smoothness:
            self.smoothness = data.smoothness
        if self.soil_dryness != data.soil_dryness:
            self.soil_dryness = data.soil_dryness

class BerryFirmness(Base, PokeApiResource):
    __tablename__ = "BerryFirmness"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    berries: Mapped[List["Berry"]] = relationship(back_populates="firmness", cascade="save-update",
                                                  primaryjoin="BerryFirmness.id == foreign(Berry.firmness_key)")
    names: Mapped[List["BerryFirmnessName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                            primaryjoin="BerryFirmness.id == foreign(BerryFirmnessName.object_key)")
    
    _cache: Dict[int, "BerryFirmness"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "berry_firmness.csv", "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_BerryFirmness_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["BerryFirmness"]:
        firmnesses = []
        for id_, firmness_data in df.iterrows():
            poke_api_id = id_
            name = firmness_data.identifier
            firmness = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[firmness.poke_api_id] = firmness
            firmnesses.append(firmness)
        return firmnesses
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

class BerryFlavor(Base, CSVResource):
    __tablename__ = "BerryFlavor"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    flavor: Mapped[int] = mapped_column(TinyInteger)
    contest_type_key: Mapped[int] = mapped_column(Integer)
    berry_key: Mapped[int] = mapped_column(Integer)

    contest_type: Mapped["ContestType"] = relationship(back_populates="berry_flavor", cascade="save-update",
                                                       primaryjoin="BerryFlavor.contest_type_key == ContestType.id",
                                                       foreign_keys=contest_type_key)
    
    berry: Mapped["Berry"] = relationship(back_populates="flavor_map",  cascade="save-update",
                                          primaryjoin="BerryFlavor.berry_key == Berry.id", foreign_keys=berry_key)
    
    _cache: Dict[int, "BerryFlavor"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "berry_flavors.csv", 
                                   "relationships": {"berry_id": ManyToOneAttrs("berry","berry_key"),
                                                     "contest_type_id": ManyToOneAttrs("contest_type", "contest_type_key")}})

    __table_args__ = (
        UniqueConstraint("berry_key","contest_type_key",name="ux_BerryFlavor_Berry_Contest"),
    )

    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.flavor = data.flavor
    
    def compare(self, data):
        if self.flavor != data.flavor:
            self.flavor = data.flavor

    def get_unique_key(self) -> str:
        return str(self.berry.poke_api_id) + ":" + str(self.contest_type.poke_api_id)