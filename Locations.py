from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Computed, UniqueConstraint, Index, Boolean

from Base import Base, TinyInteger, RegionToVersionGroupLink

if TYPE_CHECKING:
    from Encounters import Encounter, EncounterMethod
    from Evolution import EvolutionDetail
    from Games import Generation, Pokedex, VersionGroup, Version, LocationGameIndex
    from Pokemon import Pokemon, PokemonSpecies
    from TextEntries import LocationName, LocationAreaName, PalParkAreaName

class Location(Base):
    __tablename__ = "Location"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    region_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))

    region: Mapped["Region"] = relationship(back_populates="locations",
                                            primaryjoin="Location.region_key == Region.id",
                                            foreign_keys=region_key)
    names: Mapped[List["LocationName"]] = relationship(back_populates="object_ref",
                                                       primaryjoin="Location.id == foreign(LocationName.object_key)")
    game_indices: Mapped[List["LocationGameIndex"]] = relationship(back_populates="object_ref",
                                                                   primaryjoin="Location.id == foreign(LocationGameIndex.object_key)")
    areas: Mapped[List["LocationArea"]] = relationship(back_populates="location",
                                                       primaryjoin="Location.id == foreign(LocationArea.location_key)")
    evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="location",
                                                                      primaryjoin="Location.id == foreign(EvolutionDetail.location_key)")

class LocationArea(Base):
    __tablename__ = "LocationArea"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    game_index: Mapped[int] = mapped_column(TinyInteger)
    location_key: Mapped[int] = mapped_column(Integer)

    location: Mapped["Location"] = relationship(back_populates="areas",
                                                primaryjoin="LocationArea.location_key == Location.id",
                                                foreign_keys=location_key)
    encounter_method_rates: Mapped[List["EncounterMethodRate"]] = relationship(back_populates="location_area",
                                                                               primaryjoin="LocationArea.id == foreign(EncounterMethodRate.location_area_key)")
    pokemon_encounters: Mapped[List["PokemonEncounter"]] = relationship(back_populates="location_area",
                                                                        primaryjoin="LocationArea.id == foreign(PokemonEncounter.location_area_key)")
    names: Mapped[List["LocationAreaName"]] = relationship(back_populates="object_ref",
                                                           primaryjoin="LocationArea.id == foreign(LocationAreaName.object_key)")

class EncounterMethodRate(Base):
    __tablename__ = "EncounterMethodRate"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    rate: Mapped[int] = mapped_column(TinyInteger)
    location_area_key: Mapped[int] = mapped_column(Integer)
    encounter_method_key: Mapped[int] = mapped_column(Integer)
    version_key: Mapped[int] = mapped_column(Integer)

    location_area: Mapped["LocationArea"] = relationship(back_populates="encounter_method_rates",
                                                         primaryjoin="EncounterMethodRate.location_area_key == LocationArea.id",
                                                         foreign_keys=location_area_key)
    encounter_method: Mapped["EncounterMethod"] = relationship(primaryjoin="EncounterMethodRate.encounter_method_key == EncounterMethod.id",
                                                               foreign_keys=encounter_method_key)
    version: Mapped["Version"] = relationship(primaryjoin="EncounterMethodRate.version_key == Version.id",
                                              foreign_keys=version_key)

class PokemonEncounter(Base):
    __tablename__ = "PokemonEncounter"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    max_chance: Mapped[int] = mapped_column(TinyInteger)
    pokemon_key: Mapped[int] = mapped_column(Integer)
    version_key: Mapped[int] = mapped_column(Integer)
    location_area_key: Mapped[int] = mapped_column(Integer)

    pokemon: Mapped["Pokemon"] = relationship(back_populates="pokemon_encounters",
                                            primaryjoin="Pokemon.id == PokemonEncounter.pokemon_key",
                                            foreign_keys=pokemon_key)
    version: Mapped["Version"] = relationship
    encounter_details: Mapped[List["Encounter"]] = relationship(back_populates="pokemon_encounter",
                                                                primaryjoin="PokemonEncounter.id == foreign(Encounter.pokemon_encounter_key)")
    location_area: Mapped["LocationArea"] = relationship(back_populates="pokemon_encounters",
                                                         primaryjoin="PokemonEncounter.location_area_key == LocationArea.id",
                                                         foreign_keys=location_area_key)

class PalParkArea(Base):
    __tablename__ = "PalParkArea"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    names: Mapped[List["PalParkAreaName"]] = relationship(back_populates="object_ref",
                                                           primaryjoin="PalParkArea.id == foreign(PalParkAreaName.object_key)")
    pokemon_encounters: Mapped[List["PalParkEncounter"]] = relationship(back_populates="pal_park_area",
                                                                        primaryjoin="PalParkArea.id == foreign(PalParkEncounter.pal_park_area_key)")

class PalParkEncounter(Base):
    __tablename__ = "PalParkEncounter"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    base_score: Mapped[int] = mapped_column(TinyInteger)
    rarity: Mapped[int] = mapped_column(TinyInteger)
    pal_park_area_key: Mapped[int] = mapped_column(Integer)
    pokemon_species_key: Mapped[int] = mapped_column(Integer)

    pal_park_area: Mapped["PalParkArea"] = relationship(back_populates="pokemon_encounters",
                                                        primaryjoin="PalParkEncounter.pal_park_area_key == PalParkArea.id",
                                                        foreign_keys=pal_park_area_key)
    pokemon_species: Mapped["PokemonSpecies"] = relationship(back_populates="pal_park_encounters",
                                                             primaryjoin="PalParkEncounter.pokemon_species_key == PokemonSpecies.id",
                                                             foreign_keys=pokemon_species_key)

class Region(Base):
    __tablename__ = "Region"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    generation_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))

    main_generation: Mapped["Generation"] = relationship(#back_populates="region",
                                                    primaryjoin="Region.generation_key == Generation.id",
                                                    foreign_keys=generation_key)
    locations: Mapped[List["Location"]] = relationship(back_populates="region",
                                                       primaryjoin="Region.id == foreign(Location.region_key)")
    pokedexes: Mapped[List["Pokedex"]] = relationship(back_populates="region",
                                                      primaryjoin="Region.id == foreign(Pokedex.region_key)")
    versions: Mapped[List["VersionGroup"]] = relationship(back_populates="regions",secondary=RegionToVersionGroupLink)