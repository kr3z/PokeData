from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Computed, UniqueConstraint, Index, Boolean, Table, Column, ForeignKey

from Base import Base, TinyInteger, MoveLearnMethodToVersionGroupLink, RegionToVersionGroupLink, PokedexToVersionGroupLink

if TYPE_CHECKING:
    from TextEntries import PokedexDescription, PokedexName, GenerationName, VersionName
    from Pokemon import PokemonAbility, PokemonSpecies, PokemonType, PastTypeLink, Pokemon
    from Locations import Region, Location
    from Items import Item
    from Moves import Move, MoveLearnMethod, Machine

class Generation(Base):
    __tablename__ = "Generation"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    region_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))

    main_region: Mapped["Region"] = relationship(#back_populates="generation",
                                            primaryjoin="Generation.region_key == Region.id",
                                            foreign_keys=region_key)

    version_groups: Mapped[List["VersionGroup"]] = relationship(back_populates="generation",
                                                                primaryjoin="Generation.id == foreign(VersionGroup.generation_key)")
    abilities: Mapped[List["PokemonAbility"]] = relationship(back_populates="generation",
                                                           primaryjoin="Generation.id == foreign(PokemonAbility.generation_key)")
    moves: Mapped[List["Move"]] = relationship(back_populates="generation",
                                               primaryjoin="Generation.id == foreign(Move.generation_key)")
    pokemon_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="generation",
                                                           primaryjoin="Generation.id == foreign(PokemonSpecies.generation_key)")
    types_introduced: Mapped[List["PokemonType"]] = relationship(back_populates="generation_introduced",
                                                                 primaryjoin="Generation.id == foreign(PokemonType.generation_introduced_key)")
    #past_types: Mapped[List["PastTypeLink"]] = relationship

    names: Mapped[List["GenerationName"]] = relationship(back_populates="object_ref",
                                                         primaryjoin="Generation.id == foreign(GenerationName.object_key)")

class Pokedex(Base):
    __tablename__ = "Pokedex"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    region_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    is_main_series: Mapped[bool] = mapped_column(Boolean)
    #description: Mapped[str] = mapped_column(String(500)) #(extract en languate from descriptions object)    

    region: Mapped["Region"] = relationship(back_populates="pokedexes",
                                            primaryjoin="Pokedex.region_key == Region.id",
                                            foreign_keys=region_key)
    entries: Mapped[List["PokedexEntry"]] = relationship(back_populates="pokedex",
                                                         primaryjoin="Pokedex.id == foreign(PokedexEntry.pokedex_key)")
    versions: Mapped[List["VersionGroup"]] = relationship(back_populates="pokedexes", secondary=PokedexToVersionGroupLink)

    names: Mapped[List["PokedexName"]] = relationship(back_populates="object_ref",
                                                      primaryjoin="Pokedex.id == foreign(PokedexName.object_key)")
    descriptions: Mapped[List["PokedexDescription"]] = relationship(back_populates="object_ref",
                                                      primaryjoin="Pokedex.id == foreign(PokedexDescription.object_key)")

class PokedexEntry(Base):
    __tablename__ = "PokedexEntry"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    pokedex_key: Mapped[int] = mapped_column(Integer)
    pokemon_species_key: Mapped[int] = mapped_column(Integer)
    entry_number: Mapped[int] = mapped_column(Integer)

    pokedex: Mapped["Pokedex"] = relationship(back_populates="entries",
                                              primaryjoin="PokedexEntry.pokedex_key == Pokedex.id",
                                              foreign_keys=pokedex_key)
    pokemon: Mapped["PokemonSpecies"] = relationship(back_populates="pokedex_entries",
                                              primaryjoin="PokemonSpecies.id == PokedexEntry.pokemon_species_key",
                                              foreign_keys=pokemon_species_key)

class Version(Base):
    __tablename__ = "Version"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    version_group_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))

    version_group: Mapped["VersionGroup"] = relationship(back_populates="versions",
                                                         primaryjoin="Version.version_group_key == VersionGroup.id",
                                                         foreign_keys=version_group_key)

    names: Mapped[List["VersionName"]] = relationship(back_populates="object_ref",
                                                      primaryjoin="Version.id == foreign(VersionName.object_key)")

class VersionGroup(Base):
    __tablename__ = "VersionGroup"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    generation_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(Integer)

    generation: Mapped["Generation"] = relationship(back_populates="version_groups",
                                                    primaryjoin="VersionGroup.generation_key == Generation.id",
                                                    foreign_keys=generation_key)
    move_learn_methods: Mapped[List["MoveLearnMethod"]] = relationship(back_populates="version_groups", secondary=MoveLearnMethodToVersionGroupLink)
    machines: Mapped[List["Machine"]] = relationship(back_populates="version_group",
                                                    primaryjoin="VersionGroup.id == foreign(Machine.version_group_key)")
    versions: Mapped[List["Version"]] = relationship(back_populates="version_group",
                                                     primaryjoin="VersionGroup.id == foreign(Version.version_group_key)")

    # Most versions only have a single region
    # But gold/silve/crystal have both johto + kanto
    # which results in this being many-to-many
    regions: Mapped[List["Region"]] = relationship(back_populates="versions", secondary=RegionToVersionGroupLink)

    # this would be many-to-many, should it be?
    # Do any version groups actually link to multiple pokedexes?
    # If so, need link table
    pokedexes: Mapped[List["Pokedex"]] = relationship(back_populates="versions",secondary=PokedexToVersionGroupLink)

# Base GameIndex table
class GameIndex(Base):
    __tablename__ = "GameIndex"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    game_index: Mapped[int] = mapped_column(TinyInteger)
    type: Mapped[str] = mapped_column(String(30))

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_abstract": True
    }

# Abstract types
class GenerationGameIndex(GameIndex):
    generation_key: Mapped[int] = mapped_column(Integer, nullable=True)
    generation: Mapped["Generation"] = relationship(primaryjoin="GenerationGameIndex.generation_key == Generation.id",
                                                    foreign_keys=generation_key)
    __mapper_args__ = {"polymorphic_abstract": True}

class VersionGameIndex(GameIndex):
    version_key: Mapped[int] = mapped_column(Integer, nullable=True)
    version: Mapped["Version"] = relationship(primaryjoin="VersionGameIndex.version_key == Version.id",
                                              foreign_keys=version_key)
    __mapper_args__ = {"polymorphic_abstract": True}


class ItemGameIndex(GenerationGameIndex):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Item"] = relationship(back_populates="game_indices",
                                            primaryjoin="Item.id == ItemGameIndex.object_key",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "Item"}

class LocationGameIndex(GenerationGameIndex):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Location"] = relationship(back_populates="game_indices",
                                            primaryjoin="Location.id == LocationGameIndex.object_key",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "Location"}

class PokemonGameIndex(VersionGameIndex):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Pokemon"] = relationship(back_populates="game_indices",
                                            primaryjoin="Pokemon.id == PokemonGameIndex.object_key",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "Pokemon"}

class TypeGameIndex(GenerationGameIndex):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonType"] = relationship(back_populates="game_indices",
                                            primaryjoin="PokemonType.id == TypeGameIndex.object_key",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonType"}