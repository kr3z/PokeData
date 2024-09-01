import pandas as pd
from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Computed, UniqueConstraint, Index, Boolean, Table, Column, ForeignKey, SmallInteger

from Base import Base, MoveLearnMethodToVersionGroupLink, RegionToVersionGroupLink, PokedexToVersionGroupLink, PokeApiResource, get_next_id, ManyToOneAttrs, CSVData, CSVResource

if TYPE_CHECKING:
    from TextEntries import PokedexDescription, PokedexName, GenerationName, VersionName
    from Pokemon import PokemonAbility, PokemonSpecies, PokemonType, Pokemon, PokemonForm
    from Locations import Region, Location
    from Items import Item
    from Moves import Move, MoveLearnMethod, Machine

class Generation(Base, PokeApiResource):
    __tablename__ = "Generation"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    region_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))

    main_region: Mapped["Region"] = relationship(back_populates="main_generation", cascade="save-update",
                                            primaryjoin="Generation.region_key == Region.id",
                                            foreign_keys=region_key)

    version_groups: Mapped[List["VersionGroup"]] = relationship(back_populates="generation", cascade="save-update",
                                                                primaryjoin="Generation.id == foreign(VersionGroup.generation_key)")
    abilities: Mapped[List["PokemonAbility"]] = relationship(back_populates="generation", cascade="save-update",
                                                           primaryjoin="Generation.id == foreign(PokemonAbility.generation_key)")
    moves: Mapped[List["Move"]] = relationship(back_populates="generation", cascade="save-update",
                                               primaryjoin="Generation.id == foreign(Move.generation_key)")
    pokemon_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="generation", cascade="save-update",
                                                           primaryjoin="Generation.id == foreign(PokemonSpecies.generation_key)")
    types_introduced: Mapped[List["PokemonType"]] = relationship(back_populates="generation_introduced", cascade="save-update",
                                                                 primaryjoin="Generation.id == foreign(PokemonType.generation_introduced_key)")
    #past_types: Mapped[List["PastTypeLink"]] = relationship

    names: Mapped[List["GenerationName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                         primaryjoin="Generation.id == foreign(GenerationName.object_key)")
    
    
    _cache: Dict[int, "Generation"] = {}
    #_csv = "generations.csv"
    #relationship_attr_map = {"main_region_id": ManyToOneAttrs("main_region","region_key")}
    csv_data: CSVData = CSVData(**{"primary_csv": "generations.csv", "relationships": {"main_region_id": ManyToOneAttrs("main_region","region_key")}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Generation_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["Generation"]:
        generations = []
        for id_, generation_data in df.iterrows():
            poke_api_id = id_
            name = generation_data.identifier
            generation = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[generation.poke_api_id] = generation
            generations.append(generation)
        return generations

    """ @classmethod
    def parse_data(cls,data) -> "Generation":
        poke_api_id = data.id_
        name = data.name

        generation = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[generation.poke_api_id] = generation
        return generation """
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        #updated = False
        if self.name != data.identifier:
            self.name = data.identifier
            #updated = True
        #return updated


class Pokedex(Base, PokeApiResource):
    __tablename__ = "Pokedex"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    region_key: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    is_main_series: Mapped[bool] = mapped_column(Boolean)
    #description: Mapped[str] = mapped_column(String(500)) #(extract en languate from descriptions object)    

    region: Mapped["Region"] = relationship(back_populates="pokedexes", cascade="save-update",
                                            primaryjoin="Pokedex.region_key == Region.id",
                                            foreign_keys=region_key)
    entries: Mapped[List["PokedexEntry"]] = relationship(back_populates="pokedex", cascade="save-update",
                                                         primaryjoin="Pokedex.id == foreign(PokedexEntry.pokedex_key)")
    version_groups: Mapped[List["VersionGroup"]] = relationship(back_populates="pokedexes", secondary=PokedexToVersionGroupLink, cascade="save-update")

    names: Mapped[List["PokedexName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="Pokedex.id == foreign(PokedexName.object_key)")
    descriptions: Mapped[List["PokedexDescription"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="Pokedex.id == foreign(PokedexDescription.object_key)")
    
    _cache: Dict[int, "Pokedex"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "pokedexes.csv", "relationships": {"region_id": ManyToOneAttrs("region","region_key")}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Pokedex_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["Pokedex"]:
        pokedexs = []
        for id_, pokedex_data in df.iterrows():
            poke_api_id = id_
            name = pokedex_data.identifier
            is_main_series = pokedex_data.is_main_series
            pokedex = cls(poke_api_id=poke_api_id, name=name, is_main_series=is_main_series)
            cls._cache[pokedex.poke_api_id] = pokedex
            pokedexs.append(pokedex)
        return pokedexs
    
    """ @classmethod
    def parse_data(cls,data) -> "Pokedex":
        poke_api_id = data.id_
        name = data.name
        is_main_series = data.is_main_series
        pokedex = cls(poke_api_id=poke_api_id, name=name, is_main_series=is_main_series)
        cls._cache[pokedex.poke_api_id] = pokedex
        return pokedex """
    
    def __init__(self, poke_api_id: int, name: str, is_main_series: bool):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.is_main_series = is_main_series

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier
        if self.is_main_series != data.is_main_series:
            self.is_main_series = data.is_main_series

class PokedexEntry(Base, CSVResource):
    __tablename__ = "PokedexEntry"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    pokedex_key: Mapped[int] = mapped_column(Integer)
    pokemon_species_key: Mapped[int] = mapped_column(Integer)
    entry_number: Mapped[int] = mapped_column(Integer)

    pokedex: Mapped["Pokedex"] = relationship(back_populates="entries", cascade="save-update",
                                              primaryjoin="PokedexEntry.pokedex_key == Pokedex.id",
                                              foreign_keys=pokedex_key)
    pokemon_species: Mapped["PokemonSpecies"] = relationship(back_populates="pokedex_entries", cascade="save-update",
                                              primaryjoin="PokemonSpecies.id == PokedexEntry.pokemon_species_key",
                                              foreign_keys=pokemon_species_key)
    
    __table_args__ = (
        UniqueConstraint("pokemon_species_key","pokedex_key",name="ux_PokedexEntry_Species_Pokedex"),
    )
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_dex_numbers.csv", 
                         "relationships": {
                             "species_id": ManyToOneAttrs("pokemon_species","pokemon_species_key"),
                             "pokedex_id": ManyToOneAttrs("pokedex","pokedex_key")
                         }})

    """ @classmethod
    def parse_data(cls,data) -> "PokedexEntry":
        entry_number = data.entry_number
        entry = cls(entry_number=entry_number)
        #cls._cache[pokedex.poke_api_id] = pokedex
        return entry """
    
    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.entry_number = data.pokedex_number

    def compare(self, data):
        if self.entry_number != data.pokedex_number:
            self.entry_number = data.pokedex_number

    def get_unique_key(self):
        return str(self.pokemon_species.poke_api_id) + ":" + str(self.pokedex.poke_api_id)

class Version(Base, PokeApiResource):
    __tablename__ = "Version"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    version_group_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))

    version_group: Mapped["VersionGroup"] = relationship(back_populates="versions", cascade="save-update",
                                                         primaryjoin="Version.version_group_key == VersionGroup.id",
                                                         foreign_keys=version_group_key)

    names: Mapped[List["VersionName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="Version.id == foreign(VersionName.object_key)")
    
    _cache: Dict[int, "Version"] = {}
    #_csv = "versions.csv"
    #relationship_attr_map = {"version_group_id": ManyToOneAttrs("version_group","version_group_key")}
    csv_data: CSVData = CSVData(**{"primary_csv": "versions.csv", "relationships": {"version_group_id": ManyToOneAttrs("version_group","version_group_key")}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Version_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["Version"]:
        versions = []
        for id_, version_data in df.iterrows():
            poke_api_id = id_
            name = version_data.identifier
            version = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[version.poke_api_id] = version
            versions.append(version)
        return versions
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

class VersionGroup(Base, PokeApiResource):
    __tablename__ = "VersionGroup"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    generation_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(Integer)

    generation: Mapped["Generation"] = relationship(back_populates="version_groups", cascade="save-update",
                                                    primaryjoin="VersionGroup.generation_key == Generation.id",
                                                    foreign_keys=generation_key)
    move_learn_methods: Mapped[List["MoveLearnMethod"]] = relationship(back_populates="version_groups", secondary=MoveLearnMethodToVersionGroupLink, cascade="save-update")
    machines: Mapped[List["Machine"]] = relationship(back_populates="version_group", cascade="save-update",
                                                    primaryjoin="VersionGroup.id == foreign(Machine.version_group_key)")
    versions: Mapped[List["Version"]] = relationship(back_populates="version_group", cascade="save-update",
                                                     primaryjoin="VersionGroup.id == foreign(Version.version_group_key)")

    # Most versions only have a single region
    # But gold/silve/crystal have both johto + kanto
    # which results in this being many-to-many
    regions: Mapped[List["Region"]] = relationship(back_populates="version_groups", secondary=RegionToVersionGroupLink, cascade="save-update")

    # this would be many-to-many, should it be?
    # Do any version groups actually link to multiple pokedexes?
    # If so, need link table
    pokedexes: Mapped[List["Pokedex"]] = relationship(back_populates="version_groups",secondary=PokedexToVersionGroupLink, cascade="save-update")

    _cache: Dict[int, "VersionGroup"] = {}
    #_csv = "version_groups.csv"
    #relationship_attr_map = {"generation_id": ManyToOneAttrs("generation","generation_key")}
    csv_data: CSVData = CSVData(**{"primary_csv": "version_groups.csv", "relationships": {"generation_id": ManyToOneAttrs("generation","generation_key")}})

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_VersionGroup_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["VersionGroup"]:
        vgs = []
        for id_, vg_data in df.iterrows():
            poke_api_id = id_
            name = vg_data.identifier
            order = vg_data.order
            vg = cls(poke_api_id=poke_api_id, name=name, order=order)
            cls._cache[vg.poke_api_id] = vg
            vgs.append(vg)
        return vgs
    
    def __init__(self, poke_api_id: int, name: str, order: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.order = order

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier
        if self.order != data.order:
            self.order = data.order


# Base GameIndex table
class GameIndex(Base):
    __tablename__ = "GameIndex"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    game_index: Mapped[int] = mapped_column(SmallInteger)
    type: Mapped[str] = mapped_column(String(30))

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_abstract": True
    }

    def __init__(self, data):
        self.id = get_next_id()
        #self.game_index = game_index
        self.game_index = data.game_index

    def compare(self, data) -> bool:
        updated = False
        if self.game_index != data.game_index:
            self.game_index = data.game_index
            updated = True
        return updated
    
    def get_unique_key(self):
        return str(self.game_index)

# Abstract types
class GenerationGameIndex(GameIndex, CSVResource):
    generation_key: Mapped[int] = mapped_column(Integer, nullable=True)
    generation: Mapped["Generation"] = relationship(primaryjoin="GenerationGameIndex.generation_key == Generation.id",
                                                    foreign_keys=generation_key, cascade="save-update")
    __mapper_args__ = {"polymorphic_abstract": True}
    relationship_attr_map = {"generation_id": ManyToOneAttrs("generation","generation_key")}

    def __init__(self, data):
        super().__init__(data)

    def get_unique_key(self):
        unique_key = super().get_unique_key()
        return unique_key + ":" + str(self.generation.poke_api_id)

class VersionGameIndex(GameIndex, CSVResource):
    version_key: Mapped[int] = mapped_column(Integer, nullable=True)
    version: Mapped["Version"] = relationship(primaryjoin="VersionGameIndex.version_key == Version.id",
                                              foreign_keys=version_key, cascade="save-update")
    __mapper_args__ = {"polymorphic_abstract": True}

    def __init__(self, data):
        super().__init__(data)

    def get_unique_key(self):
        unique_key = super().get_unique_key()
        return unique_key + ":" + str(self.version.poke_api_id)


class ItemGameIndex(GenerationGameIndex):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Item"] = relationship(back_populates="game_indices", cascade="save-update",
                                            primaryjoin="Item.id == ItemGameIndex.object_key",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "Item"}
    relationship_attr_map = dict(GenerationGameIndex.relationship_attr_map)
    relationship_attr_map.update({"item_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "item_game_indices.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)

    def get_unique_key(self):
        unique_key = super().get_unique_key()
        return unique_key + ":" + str(self.object_ref.poke_api_id)  

class LocationGameIndex(GenerationGameIndex):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Location"] = relationship(back_populates="game_indices", cascade="save-update",
                                            primaryjoin="Location.id == LocationGameIndex.object_key",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "Location"}
    relationship_attr_map = dict(GenerationGameIndex.relationship_attr_map)
    relationship_attr_map.update({"location_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "location_game_indices.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)

    def get_unique_key(self):
        unique_key = super().get_unique_key()
        return unique_key + ":" + str(self.object_ref.poke_api_id) 

class PokemonGameIndex(VersionGameIndex):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Pokemon"] = relationship(back_populates="game_indices", cascade="save-update",
                                            primaryjoin="Pokemon.id == PokemonGameIndex.object_key",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "Pokemon"}

    def __init__(self, data):
        super().__init__(data)

    def get_unique_key(self):
        unique_key = super().get_unique_key()
        return unique_key + ":" + str(self.object_ref.poke_api_id) 

class TypeGameIndex(GenerationGameIndex):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonType"] = relationship(back_populates="game_indices", cascade="save-update",
                                            primaryjoin="PokemonType.id == TypeGameIndex.object_key",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonType"}
    relationship_attr_map = dict(GenerationGameIndex.relationship_attr_map)
    relationship_attr_map.update({"type_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "type_game_indices.csv", "relationships": relationship_attr_map})
    
    def __init__(self, data):
        super().__init__(data)

    def get_unique_key(self):
        unique_key = super().get_unique_key()
        return unique_key + ":" + str(self.object_ref.poke_api_id) 
    
class FormGameIndex(GenerationGameIndex):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonForm"] = relationship(back_populates="game_indices", cascade="save-update",
                                            primaryjoin="PokemonForm.id == FormGameIndex.object_key",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonForm"}
    relationship_attr_map = dict(GenerationGameIndex.relationship_attr_map)
    relationship_attr_map.update({"pokemon_form_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_form_generations.csv", "relationships": relationship_attr_map})
    
    def __init__(self, data):
        super().__init__(data)

    def get_unique_key(self):
        unique_key = super().get_unique_key()
        return unique_key + ":" + str(self.object_ref.poke_api_id) 
