from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Computed, UniqueConstraint, Index, Boolean

from Base import Base, TinyInteger, RegionToVersionGroupLink, PokeApiResource, get_next_id

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

    region: Mapped["Region"] = relationship(back_populates="locations", cascade="save-update",
                                            primaryjoin="Location.region_key == Region.id",
                                            foreign_keys=region_key)
    names: Mapped[List["LocationName"]] = relationship(back_populates="object_ref", cascade="save-update",
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

    location: Mapped["Location"] = relationship(back_populates="areas", cascade="save-update",
                                                primaryjoin="LocationArea.location_key == Location.id",
                                                foreign_keys=location_key)
    encounter_method_rates: Mapped[List["EncounterMethodRate"]] = relationship(back_populates="location_area",
                                                                               primaryjoin="LocationArea.id == foreign(EncounterMethodRate.location_area_key)")
    pokemon_encounters: Mapped[List["PokemonEncounter"]] = relationship(back_populates="location_area",
                                                                        primaryjoin="LocationArea.id == foreign(PokemonEncounter.location_area_key)")
    names: Mapped[List["LocationAreaName"]] = relationship(back_populates="object_ref", cascade="save-update",
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

    pokemon: Mapped["Pokemon"] = relationship(back_populates="pokemon_encounters", cascade="save-update",
                                            primaryjoin="Pokemon.id == PokemonEncounter.pokemon_key",
                                            foreign_keys=pokemon_key)
    version: Mapped["Version"] = relationship(primaryjoin="Version.id == PokemonEncounter.version_key",
                                            foreign_keys=version_key)
    encounter_details: Mapped[List["Encounter"]] = relationship(back_populates="pokemon_encounter",
                                                                primaryjoin="PokemonEncounter.id == foreign(Encounter.pokemon_encounter_key)")
    location_area: Mapped["LocationArea"] = relationship(back_populates="pokemon_encounters",
                                                         primaryjoin="PokemonEncounter.location_area_key == LocationArea.id",
                                                         foreign_keys=location_area_key)

class PalParkArea(Base, PokeApiResource):
    __tablename__ = "PalParkArea"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    names: Mapped[List["PalParkAreaName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                           primaryjoin="PalParkArea.id == foreign(PalParkAreaName.object_key)")
    pokemon_encounters: Mapped[List["PalParkEncounter"]] = relationship(back_populates="pal_park_area",
                                                                        primaryjoin="PalParkArea.id == foreign(PalParkEncounter.pal_park_area_key)")
    _cache: Dict[int, "Region"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PalParkArea_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "PalParkArea":
        poke_api_id = data.id_
        name = data.name

        area = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[area.poke_api_id] = area
        return area
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name

class PalParkEncounter(Base):
    __tablename__ = "PalParkEncounter"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    base_score: Mapped[int] = mapped_column(TinyInteger)
    #rarity: Mapped[int] = mapped_column(TinyInteger)
    rate: Mapped[int] = mapped_column(TinyInteger)
    pal_park_area_key: Mapped[int] = mapped_column(Integer)
    pokemon_species_key: Mapped[int] = mapped_column(Integer)

    pal_park_area: Mapped["PalParkArea"] = relationship(back_populates="pokemon_encounters", cascade="save-update",
                                                        primaryjoin="PalParkEncounter.pal_park_area_key == PalParkArea.id",
                                                        foreign_keys=pal_park_area_key)
    pokemon_species: Mapped["PokemonSpecies"] = relationship(back_populates="pal_park_encounters", cascade="save-update",
                                                             primaryjoin="PalParkEncounter.pokemon_species_key == PokemonSpecies.id",
                                                             foreign_keys=pokemon_species_key)
    
    __table_args__ = (
        UniqueConstraint("pokemon_species_key","pal_park_area_key",name="ux_PalParkEncounter_SpeciesKey_PalParkAreaKey"),
    )

    @classmethod
    def parse_data(cls,base_score: int, rate: int) -> "PalParkEncounter":
        #poke_api_id = data.id
        encounter = cls(base_score = base_score, rate = rate)
        #cls._cache[evolution_chain.poke_api_id] = evolution_chain
        return encounter
    
    def __init__(self, base_score: int, rate: int):
        self.id = get_next_id()
        self.base_score = base_score
        #self.rarity = rarity
        self.rate = rate

    def compare(self, base_score: int, rate: int):
        if self.base_score != base_score:
            self.base_score = base_score
        """ if self.rarity != rarity:
            self.rarity = rarity """
        if self.rate != rate:
            self.rate = rate

class Region(Base, PokeApiResource):
    __tablename__ = "Region"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    generation_key: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))

    main_generation: Mapped["Generation"] = relationship(back_populates="main_region", cascade="save-update",
                                                    primaryjoin="Region.generation_key == Generation.id",
                                                    foreign_keys=generation_key)
    locations: Mapped[List["Location"]] = relationship(back_populates="region", cascade="save-update",
                                                       primaryjoin="Region.id == foreign(Location.region_key)")
    pokedexes: Mapped[List["Pokedex"]] = relationship(back_populates="region", cascade="save-update",
                                                      primaryjoin="Region.id == foreign(Pokedex.region_key)")
    version_groups: Mapped[List["VersionGroup"]] = relationship(back_populates="regions",secondary=RegionToVersionGroupLink, cascade="save-update")

    _cache: Dict[int, "Region"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Region_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "Region":
        poke_api_id = data.id_
        name = data.name

        region = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[region.poke_api_id] = region
        return region
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name