import pandas as pd
from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Table, Column, ForeignKey, Boolean, UniqueConstraint

from Base import Base, TinyInteger, get_next_id, PokeApiResource

if TYPE_CHECKING:
    from Contests import ContestType
    from Items import Item
    from Pokemon import PokemonType, PokemonNature
    from TextEntries import BerryFirmnessName, BerryFlavorName

class Berry(Base, PokeApiResource):
    __tablename__ = "Berry"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
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

    flavors: Mapped[List["BerryFlavorLink"]] = relationship(back_populates="berry", cascade="save-update",
                                                            primaryjoin="Berry.id == foreign(BerryFlavorLink.berry_key)")
    
    _cache: Dict[int, "Berry"] = {}
    _csv = "berries.csv" # doesn't have name

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Berry_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "Berry":
        poke_api_id = data.id_
        name = data.name
        growth_time = data.growth_time
        max_harvest = data.max_harvest
        natural_gift_power = data.natural_gift_power
        size = data.size
        smoothness = data.smoothness
        soil_dryness = data.soil_dryness

        berry = cls(poke_api_id=poke_api_id, name=name, growth_time=growth_time, max_harvest=max_harvest, 
                    natural_gift_power=natural_gift_power, size=size, smoothness=smoothness, soil_dryness=soil_dryness)
        cls._cache[berry.poke_api_id] = berry
        return berry
    
    def __init__(self, poke_api_id: int, name: str, growth_time: int, max_harvest: int, 
                    natural_gift_power: int, size: int, smoothness: int, soil_dryness: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.growth_time = growth_time
        self.max_harvest = max_harvest
        self.natural_gift_power = natural_gift_power
        self.size = size
        self.smoothness = smoothness
        self.soil_dryness = soil_dryness

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name
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

class BerryFlavorLink(Base):
    __tablename__ = "BerryFlavorLink"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    potency: Mapped[int] = mapped_column(TinyInteger)
    flavor_key: Mapped[int] = mapped_column(Integer)
    berry_key: Mapped[int] = mapped_column(Integer)

    flavor: Mapped["BerryFlavor"] = relationship(back_populates="berries", cascade="save-update",
                                                 primaryjoin="BerryFlavorLink.flavor_key == BerryFlavor.id",
                                                 foreign_keys=flavor_key)
    berry: Mapped["Berry"] = relationship(back_populates="flavors", cascade="save-update",
                                          primaryjoin="BerryFlavorLink.berry_key == Berry.id",
                                          foreign_keys=berry_key)
    
    @classmethod
    def parse_data(cls,data) -> "BerryFlavorLink":
        potency = data.potency

        link = cls(potency=potency)
        #cls._cache[firmness.poke_api_id] = firmness
        return link
    
    def __init__(self, potency: int):
        self.id = get_next_id()
        self.potency = potency

    def compare(self, data):
        if self.potency != data.potency:
            self.potency = data.potency

class BerryFirmness(Base, PokeApiResource):
    __tablename__ = "BerryFirmness"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    berries: Mapped[List["Berry"]] = relationship(back_populates="firmness", cascade="save-update",
                                                  primaryjoin="BerryFirmness.id == foreign(Berry.firmness_key)")
    names: Mapped[List["BerryFirmnessName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                            primaryjoin="BerryFirmness.id == foreign(BerryFirmnessName.object_key)")
    
    _cache: Dict[int, "BerryFirmness"] = {}
    _csv = "berry_firmness.csv"
    relationship_attr_map = {}
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

class BerryFlavor(Base, PokeApiResource):
    __tablename__ = "BerryFlavor"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    contest_type_key: Mapped[int] = mapped_column(Integer)

    contest_type: Mapped["ContestType"] = relationship(back_populates="berry_flavor",
                                                       primaryjoin="BerryFlavor.contest_type_key == ContestType.id",
                                                       foreign_keys=contest_type_key)

    berries: Mapped[List["BerryFlavorLink"]] = relationship(back_populates="flavor",
                                                            primaryjoin="BerryFlavor.id == foreign(BerryFlavorLink.flavor_key)")
    
    names: Mapped[List["BerryFlavorName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                            primaryjoin="BerryFlavor.id == foreign(BerryFlavorName.object_key)")

    hates_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="hates_flavor", cascade="save-update",
                                                              primaryjoin="BerryFlavor.id == foreign(PokemonNature.hates_flavor_key)")
    likes_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="likes_flavor", cascade="save-update",
                                                              primaryjoin="BerryFlavor.id == foreign(PokemonNature.likes_flavor_key)")
    
    _cache: Dict[int, "BerryFlavor"] = {}
    _csv = "berry_flavors.csv" # missing data!

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_BerryFlavor_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "BerryFlavor":
        poke_api_id = data.id_
        name = data.name

        flavor = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[flavor.poke_api_id] = flavor
        return flavor
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name