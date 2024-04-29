from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Table, Column, ForeignKey, Boolean

from Base import Base, TinyInteger

if TYPE_CHECKING:
    from Contests import ContestType
    from Items import Item
    from Pokemon import PokemonType, PokemonNature
    from TextEntries import BerryFirmnessName, BerryFlavorName

class Berry(Base):
    __tablename__ = "Berry"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    growth_time: Mapped[int] = mapped_column(TinyInteger)
    max_harvest: Mapped[int] = mapped_column(TinyInteger)
    natural_gift_power: Mapped[int] = mapped_column(TinyInteger)
    size: Mapped[int] = mapped_column(TinyInteger)
    smoothness: Mapped[int] = mapped_column(TinyInteger)
    soil_dryness: Mapped[int] = mapped_column(TinyInteger)
    firmness_key: Mapped[int] = mapped_column(Integer)
    item_key: Mapped[int] = mapped_column(Integer)
    natural_gift_type_key: Mapped[int] = mapped_column(Integer)

    firmness: Mapped["BerryFirmness"] = relationship(back_populates="berries",
                                                     primaryjoin="Berry.firmness_key == BerryFirmness.id",
                                                     foreign_keys=firmness_key)
    item: Mapped["Item"] = relationship(#back_populates="berry",
                                        primaryjoin="Berry.item_key == Item.id",
                                        foreign_keys=item_key)
    natural_gift_type: Mapped["PokemonType"] = relationship(primaryjoin="Berry.natural_gift_type_key == PokemonType.id",
                                                            foreign_keys=natural_gift_type_key)

    flavors: Mapped[List["BerryFlavorLink"]] = relationship(back_populates="berry",
                                                            primaryjoin="Berry.id == foreign(BerryFlavorLink.berry_key)")

class BerryFlavorLink(Base):
    __tablename__ = "BerryFlavorLink"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    potency: Mapped[int] = mapped_column(TinyInteger)
    flavor_key: Mapped[int] = mapped_column(Integer)
    berry_key: Mapped[int] = mapped_column(Integer)

    flavor: Mapped["BerryFlavor"] = relationship(back_populates="berries",
                                                 primaryjoin="BerryFlavorLink.flavor_key == BerryFlavor.id",
                                                 foreign_keys=flavor_key)
    berry: Mapped["Berry"] = relationship(back_populates="flavors",
                                          primaryjoin="BerryFlavorLink.berry_key == Berry.id",
                                          foreign_keys=berry_key)

class BerryFirmness(Base):
    __tablename__ = "BerryFirmness"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    berries: Mapped[List["Berry"]] = relationship(back_populates="firmness",
                                                  primaryjoin="BerryFirmness.id == foreign(Berry.firmness_key)")
    names: Mapped[List["BerryFirmnessName"]] = relationship(back_populates="object_ref",
                                                            primaryjoin="BerryFirmness.id == foreign(BerryFirmnessName.object_key)")

class BerryFlavor(Base):
    __tablename__ = "BerryFlavor"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    contest_type_key: Mapped[int] = mapped_column(Integer)

    contest_type: Mapped["ContestType"] = relationship(#back_populates="berry_flavor",
                                                       primaryjoin="BerryFlavor.contest_type_key == ContestType.id",
                                                       foreign_keys=contest_type_key)

    berries: Mapped[List["BerryFlavorLink"]] = relationship(back_populates="flavor",
                                                            primaryjoin="BerryFlavor.id == foreign(BerryFlavorLink.flavor_key)")
    
    names: Mapped[List["BerryFlavorName"]] = relationship(back_populates="object_ref",
                                                            primaryjoin="BerryFlavor.id == foreign(BerryFlavorName.object_key)")

    hates_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="hates_flavor",
                                                              primaryjoin="BerryFlavor.id == foreign(PokemonNature.hates_flavor_key)")
    likes_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="likes_flavor",
                                                              primaryjoin="BerryFlavor.id == foreign(PokemonNature.likes_flavor_key)")