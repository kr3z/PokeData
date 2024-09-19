import pandas as pd
from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Computed, UniqueConstraint, Boolean, SmallInteger

from Base import Base, TinyInteger, get_next_id, PokeApiResource, CSVData, CSVResource, ManyToOneAttrs, MergeCSV, FilterCSV, FilterOperation, SpeciesToEggGroupLink, GroupByCSV, ManyToManyAttr

if TYPE_CHECKING:
    from Contests import ContestType
    from Encounters import Encounter
    from Evolution import EvolutionChain, EvolutionDetail
    from Games import Generation, PokedexEntry, Version, VersionGroup, PokemonGameIndex, TypeGameIndex, FormGameIndex
    from Items import Item
    from Moves import DamageClass, MoveBattleStyle, Move, MoveLearnMethod, MoveStatChange
    from Locations import PalParkEncounter
    from TextEntries import CharacteristicDescription, AbilityEffect, AbilityFlavorText
    from TextEntries import PokemonName, PokemonSpeciesFlavorText, PokemonFormDescription, PokemonTypeName
    from TextEntries import PokemonStatName, PokemonNatureName, PokemonAbilityName, EggGroupName
    from TextEntries import GrowthRateName, PokemonColorName, PokemonFormName, PokemonFormFormName
    from TextEntries import PokemonHabitatName, PokemonShapeAwesomeName, PokemonShapeName, PokemonGenus, PokeathlonStatName, PokemonShapeDescription, AbilityPastEffect

class PokemonAbility(Base, PokeApiResource):
    __tablename__ = "PokemonAbility"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    generation_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    is_main_series: Mapped[bool] = mapped_column(Boolean)

    generation: Mapped["Generation"] = relationship(back_populates="abilities", cascade="save-update",
                                            primaryjoin="Generation.id == PokemonAbility.generation_key",
                                            foreign_keys=generation_key)
    
    pokemon_slots: Mapped[List["PokemonAbilityLink"]] = relationship(back_populates="ability", cascade="save-update",
                                                              primaryjoin="PokemonAbility.id == foreign(PokemonAbilityLink.ability_key)")

    names: Mapped[List["PokemonAbilityName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="PokemonAbility.id == foreign(PokemonAbilityName.object_key)")
    effect_entries: Mapped[List["AbilityEffect"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="PokemonAbility.id == foreign(AbilityEffect.object_key)")
    flavor_text_entries: Mapped[List["AbilityFlavorText"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="PokemonAbility.id == foreign(AbilityFlavorText.object_key)")
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonAbility_PokeApiId"),
    )

    _cache: Dict[int, "PokemonAbility"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "abilities.csv", 
                                   "relationships": {"generation_id": ManyToOneAttrs("generation","generation_key")}})
    
    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonAbility"]:
        abilities = []
        for id_, ability_data in df.iterrows():
            poke_api_id = id_
            name = ability_data.identifier
            is_main_series = ability_data.is_main_series
            ability = cls(poke_api_id=poke_api_id, name=name, is_main_series=is_main_series)
            cls._cache[ability.poke_api_id] = ability
            abilities.append(ability)
        return abilities
    
    def __init__(self, poke_api_id: int, name: str, is_main_series: bool = is_main_series):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.is_main_series = is_main_series

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier
        if self.is_main_series != data.is_main_series:
            self.is_main_series = data.is_main_series

class PokemonAbilityPastEffect(Base, PokeApiResource):
    __tablename__ = "PokemonAbilityPastEffect"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    ability_key: Mapped[int] = mapped_column(Integer)
    changed_in_version_group_key: Mapped[int] = mapped_column(Integer)

    ability: Mapped["PokemonAbility"] = relationship(cascade="save-update",
                                            primaryjoin="PokemonAbility.id == PokemonAbilityPastEffect.ability_key",
                                            foreign_keys=ability_key)
    changed_in_version_group: Mapped["VersionGroup"] = relationship(cascade="save-update",
                                            primaryjoin="VersionGroup.id == PokemonAbilityPastEffect.changed_in_version_group_key",
                                            foreign_keys=changed_in_version_group_key)
    
    effect_entries: Mapped[List["AbilityPastEffect"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="PokemonAbilityPastEffect.id == foreign(AbilityPastEffect.object_key)")
    
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonAbilityPastEffect_PokeApiId"),
    )

    _cache: Dict[int, "PokemonAbilityPastEffect"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "ability_changelog.csv", 
                                   "relationships": {"ability_id": ManyToOneAttrs("ability","ability_key"),
                                                     "changed_in_version_group_id": ManyToOneAttrs("changed_in_version_group","changed_in_version_group_key")}})

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonAbilityPastEffect"]:
        abilities = []
        for id_, ability_data in df.iterrows():
            poke_api_id = id_
            ability = cls(poke_api_id=poke_api_id)
            cls._cache[ability.poke_api_id] = ability
            abilities.append(ability)
        return abilities
    
    def __init__(self, poke_api_id: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id

    def compare(self, data):
        pass
    

class PokemonCharacteristic(Base, PokeApiResource):
    __tablename__ = "PokemonCharacteristic"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    highest_stat_key: Mapped[int] = mapped_column(Integer)
    gene_modulo: Mapped[int] = mapped_column(TinyInteger)

    highest_stat: Mapped["PokemonStat"] = relationship(back_populates="characteristics", cascade="save-update",
                                            primaryjoin="PokemonStat.id == PokemonCharacteristic.highest_stat_key",
                                            foreign_keys=highest_stat_key)
    descriptions: Mapped[List["CharacteristicDescription"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="PokemonCharacteristic.id == foreign(CharacteristicDescription.object_key)")
    
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonCharacteristic_PokeApiId"),
    )

    _cache: Dict[int, "PokemonCharacteristic"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "characteristics.csv", 
                                   "relationships": {"stat_id": ManyToOneAttrs("highest_stat","highest_stat_key")}})

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonCharacteristic"]:
        characteristics = []
        for id_, characteristic_data in df.iterrows():
            poke_api_id = id_
            gene_modulo = characteristic_data.gene_mod_5
            characteristic = cls(poke_api_id=poke_api_id, gene_modulo=gene_modulo)
            cls._cache[characteristic.poke_api_id] = characteristic
            characteristics.append(characteristic)
        return characteristics
    
    def __init__(self, poke_api_id: int, gene_modulo: int = gene_modulo):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.gene_modulo = gene_modulo

    def compare(self, data):
        if self.gene_modulo != data.gene_mod_5:
            self.gene_modulo = data.gene_mod_5

class EggGroup(Base, PokeApiResource):
    __tablename__ = "EggGroup"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    #poke_api_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))

    names: Mapped[List["EggGroupName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                        primaryjoin="EggGroup.id == foreign(EggGroupName.object_key)")
    
    species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="egg_groups", secondary=SpeciesToEggGroupLink, cascade="save-update")

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EggGroup_PokeApiId"),
    )

    _cache: Dict[int, "EggGroup"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "egg_groups.csv", 
                                   "relationships": {}})

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["EggGroup"]:
        eggs = []
        for id_, egg_data in df.iterrows():
            poke_api_id = id_
            name = egg_data.identifier
            egg = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[egg.poke_api_id] = egg
            eggs.append(egg)
        return eggs
    
    def __init__(self, poke_api_id: int, name: str,):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

class GrowthRate(Base, PokeApiResource):
    __tablename__ = "GrowthRate"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    formula: Mapped[str] = mapped_column(String(500))

    names: Mapped[List["GrowthRateName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="GrowthRate.id == foreign(GrowthRateName.object_key)")
    levels: Mapped[List["GrowthRateExperienceLevel"]] = relationship(back_populates="growth_rate", cascade="save-update",
                                                              primaryjoin="GrowthRate.id == foreign(GrowthRateExperienceLevel.growth_rate_key)")
    pokemon_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="growth_rate", cascade="save-update",
                                                              primaryjoin="GrowthRate.id == foreign(PokemonSpecies.growth_rate_key)")
    
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_GrowthRate_PokeApiId"),
    )

    _cache: Dict[int, "GrowthRate"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "growth_rates.csv", 
                                   "relationships": {}})
    
    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["GrowthRate"]:
        rates = []
        for id_, rate_data in df.iterrows():
            poke_api_id = id_
            name = rate_data.identifier
            formula = rate_data.formula
            rate = cls(poke_api_id=poke_api_id, name=name, formula=formula)
            cls._cache[rate.poke_api_id] = rate
            rates.append(rate)
        return rates
    
    def __init__(self, poke_api_id: int, name: str, formula: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.formula = formula

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier
        if self.formula != data.formula:
            self.formula = data.formula

class GrowthRateExperienceLevel(Base):
    __tablename__ = "GrowthRateExperienceLevel"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    growth_rate_key: Mapped[int] = mapped_column(Integer)
    level: Mapped[int] = mapped_column(TinyInteger)
    experience: Mapped[int] = mapped_column(Integer)

    growth_rate: Mapped["GrowthRate"] = relationship(back_populates="levels", cascade="save-update",
                                            primaryjoin="GrowthRate.id == GrowthRateExperienceLevel.growth_rate_key",
                                            foreign_keys=growth_rate_key)
    
    __table_args__ = (
        UniqueConstraint("growth_rate_key","level",name="ux_GrowthRateXP_rate_level"),
    )
    csv_data: CSVData = CSVData(**{"primary_csv": "experience.csv",
                          "relationships": {
                                            "growth_rate_id": ManyToOneAttrs("growth_rate", "growth_rate_key")},
                            "append_unique_attrs":("level",)})
    
    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.level = data.level
        self.experience = data.experience

    def compare(self, data):
        if self.level != data.level:
            self.level = data.level
        if self.experience != data.experience:
            self.experience = data.experience

    def get_unique_key(self):
        return str(self.level) + ":" + str(self.growth_rate.poke_api_id)

class PokemonNature(Base, PokeApiResource):
    __tablename__ = "PokemonNature"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    decreased_stat_key: Mapped[int] = mapped_column(Integer)
    increased_stat_key: Mapped[int] = mapped_column(Integer)
    decreased_pokeathlon_stat_key: Mapped[int] = mapped_column(Integer)
    increased_pokeathlon_stat_key: Mapped[int] = mapped_column(Integer)
    hates_flavor_key: Mapped[int] = mapped_column(Integer)
    likes_flavor_key: Mapped[int] = mapped_column(Integer)
    max_pokeathlon_increase: Mapped[int] = mapped_column(Integer)
    max_pokeathlon_decrease: Mapped[int] = mapped_column(Integer)
    game_index: Mapped[int] = mapped_column(TinyInteger)

    decreased_stat: Mapped["PokemonStat"] = relationship(back_populates="decreasing_natures", cascade="save-update",
                                            primaryjoin="PokemonStat.id == PokemonNature.decreased_stat_key",
                                            foreign_keys=decreased_stat_key)
    increased_stat: Mapped["PokemonStat"] = relationship(back_populates="increasing_natures", cascade="save-update",
                                            primaryjoin="PokemonStat.id == PokemonNature.increased_stat_key",
                                            foreign_keys=increased_stat_key)
    decreased_pokeathlon_stat: Mapped["PokeathlonStat"] = relationship(back_populates="decreasing_natures", cascade="save-update",
                                            primaryjoin="PokeathlonStat.id == PokemonNature.decreased_pokeathlon_stat_key",
                                            foreign_keys=decreased_pokeathlon_stat_key)
    increased_pokeathlon_stat: Mapped["PokeathlonStat"] = relationship(back_populates="increasing_natures", cascade="save-update",
                                            primaryjoin="PokeathlonStat.id == PokemonNature.increased_pokeathlon_stat_key",
                                            foreign_keys=increased_pokeathlon_stat_key)
    hates_flavor: Mapped["ContestType"] = relationship(back_populates="hates_natures", cascade="save-update",
                                            primaryjoin="ContestType.id == PokemonNature.hates_flavor_key",
                                            foreign_keys=hates_flavor_key)
    likes_flavor: Mapped["ContestType"] = relationship(back_populates="likes_natures", cascade="save-update",
                                            primaryjoin="ContestType.id == PokemonNature.likes_flavor_key",
                                            foreign_keys=likes_flavor_key)

    move_battle_style_preferences: Mapped[List["MoveBattleStylePreference"]] = relationship(back_populates="pokemon_nature",
                                                              primaryjoin="PokemonNature.id == foreign(MoveBattleStylePreference.pokemon_nature_key)")

    names: Mapped[List["PokemonNatureName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="PokemonNature.id == foreign(PokemonNatureName.object_key)")
    
    _cache: Dict[int, "PokemonNature"] = {}

    csv_data: CSVData = CSVData(**{"primary_csv": "natures.csv", 
                        "relationships": {
                            "decreased_stat_id": ManyToOneAttrs("decreased_stat","decreased_stat_key"),
                            "increased_stat_id": ManyToOneAttrs("increased_stat","increased_stat_key"),
                            "hates_flavor_id": ManyToOneAttrs("hates_flavor","hates_flavor_key"),
                            "likes_flavor_id": ManyToOneAttrs("likes_flavor","likes_flavor_key"),
                            "decreased_pokeathlon_stat_id": ManyToOneAttrs("decreased_pokeathlon_stat", "decreased_pokeathlon_stat_key"),
                            "increased_pokeathlon_stat_id": ManyToOneAttrs("increased_pokeathlon_stat","increased_pokeathlon_stat_key")},
                        "merge_csvs": (MergeCSV("nature_pokeathlon_stats.csv", "nature_id", 
                                                rename_columns={"pokeathlon_stat_id": "decreased_pokeathlon_stat_id", 
                                                                "max_change": "max_pokeathlon_decrease"},
                                                filter=FilterCSV("max_change", FilterOperation.LESSTHAN, 0)),
                                        MergeCSV("nature_pokeathlon_stats.csv", "nature_id", 
                                                rename_columns={"pokeathlon_stat_id": "increased_pokeathlon_stat_id", 
                                                                "max_change": "max_pokeathlon_increase"},
                                                filter=FilterCSV("max_change", FilterOperation.GREATERTHAN, 0)))})

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonNature_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonNature"]:
        natures = []
        for id_, nature_data in df.iterrows():
            poke_api_id = id_
            name = nature_data.identifier
            game_index = nature_data.game_index
            max_pokeathlon_decrease = nature_data.max_pokeathlon_decrease
            max_pokeathlon_increase = nature_data.max_pokeathlon_increase

            nature = cls(poke_api_id=poke_api_id, name=name, game_index=game_index, max_pokeathlon_decrease=max_pokeathlon_decrease, max_pokeathlon_increase=max_pokeathlon_increase)
            cls._cache[nature.poke_api_id] = nature
            natures.append(nature)
        return natures
    
    def __init__(self, poke_api_id: int, name: str, game_index: int, max_pokeathlon_decrease: int, max_pokeathlon_increase: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.game_index = game_index
        self.max_pokeathlon_decrease = max_pokeathlon_decrease
        self.max_pokeathlon_increase = max_pokeathlon_increase

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name
        if self.game_index != data.game_index:
            self.game_index = data.game_index
        if self.max_pokeathlon_decrease != data.max_pokeathlon_decrease:
            self.max_pokeathlon_decrease = data.max_pokeathlon_decrease
        if self.max_pokeathlon_increase != data.max_pokeathlon_increase:
            self.max_pokeathlon_increase = data.max_pokeathlon_increase

class MoveBattleStylePreference(Base, CSVResource):
    __tablename__ = "MoveBattleStylePreference"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    move_battle_style_key: Mapped[int] = mapped_column(Integer)
    pokemon_nature_key: Mapped[int] = mapped_column(Integer)
    low_hp_preference: Mapped[int] = mapped_column(TinyInteger)
    high_hp_preference: Mapped[int] = mapped_column(TinyInteger)

    move_battle_style: Mapped["MoveBattleStyle"] = relationship(back_populates="preference", cascade="save-update",
                                            primaryjoin="MoveBattleStyle.id == MoveBattleStylePreference.move_battle_style_key",
                                            foreign_keys=move_battle_style_key)
    pokemon_nature: Mapped["PokemonNature"] = relationship(back_populates="move_battle_style_preferences", cascade="save-update",
                                            primaryjoin="PokemonNature.id == MoveBattleStylePreference.pokemon_nature_key",
                                            foreign_keys=pokemon_nature_key)

    csv_data: CSVData = CSVData(**{"primary_csv": "nature_battle_style_preferences.csv", 
                        "relationships": {
                            "nature_id": ManyToOneAttrs("pokemon_nature","pokemon_nature_key"),
                            "move_battle_style_id": ManyToOneAttrs("move_battle_style","move_battle_style_key")}})

    __table_args__ = (
        UniqueConstraint("pokemon_nature_key","move_battle_style_key",name="ux_MBSP_Nature_MBS"),
    )

    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.low_hp_preference = data.low_hp_preference
        self.high_hp_preference = data.high_hp_preference

    def compare(self, data):
        if self.low_hp_preference != data.low_hp_preference:
            self.low_hp_preference = data.low_hp_preference
        if self.high_hp_preference != data.high_hp_preference:
            self.high_hp_preference = data.high_hp_preference

    def get_unique_key(self):
        return str(self.pokemon_nature.poke_api_id) + ":" + str(self.move_battle_style.poke_api_id)

class PokeathlonStat(Base, PokeApiResource):
    __tablename__ = "PokeathlonStat"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    decreasing_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="decreased_pokeathlon_stat", cascade="save-update",
                                                              primaryjoin="PokeathlonStat.id == foreign(PokemonNature.decreased_pokeathlon_stat_key)")
    increasing_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="increased_pokeathlon_stat", cascade="save-update",
                                                              primaryjoin="PokeathlonStat.id == foreign(PokemonNature.increased_pokeathlon_stat_key)")

    names: Mapped[List["PokeathlonStatName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                          primaryjoin="PokeathlonStat.id == foreign(PokeathlonStatName.object_key)")
    
    _cache: Dict[int, "PokeathlonStat"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "pokeathlon_stats.csv", 
                         "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokeathlonStat_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokeathlonStat"]:
        stats = []
        for id_, stat_data in df.iterrows():
            poke_api_id = id_
            name = stat_data.identifier
            stat = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[stat.poke_api_id] = stat
            stats.append(stat)
        return stats
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier


class Pokemon(Base, PokeApiResource):
    __tablename__ = "Pokemon"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    species_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    base_experience: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    weight: Mapped[int] = mapped_column(Integer)
    is_default: Mapped[bool] = mapped_column(Boolean)
    order: Mapped[Optional[int]] = mapped_column(Integer)

    hp: Mapped[int] = mapped_column(Integer)
    attack: Mapped[int] = mapped_column(Integer)
    defense: Mapped[int] = mapped_column(Integer)
    special_attack: Mapped[int] = mapped_column(Integer)
    special_defense: Mapped[int] = mapped_column(Integer)
    speed: Mapped[int] = mapped_column(Integer)
    bst: Mapped[int] = mapped_column(Integer,Computed('hp+attack+defense+special_attack+special_defense+speed',persisted=False))

    hp_ev: Mapped[Optional[int]] = mapped_column(Integer)
    attack_ev: Mapped[Optional[int]] = mapped_column(Integer)
    defense_ev: Mapped[Optional[int]] = mapped_column(Integer)
    special_attack_ev: Mapped[Optional[int]] = mapped_column(Integer)
    special_defense_ev: Mapped[Optional[int]] = mapped_column(Integer)
    speed_ev: Mapped[Optional[int]] = mapped_column(Integer)

    species: Mapped["PokemonSpecies"] = relationship(back_populates="varieties", cascade="save-update",
                                            primaryjoin="Pokemon.species_key == PokemonSpecies.id",
                                            foreign_keys=species_key)
    
    type_slots: Mapped[List["AbstractPokemonTypeLink"]] = relationship(back_populates="pokemon", cascade="save-update",
                                                         primaryjoin="foreign(AbstractPokemonTypeLink.object_key) == Pokemon.id")

    ability_slots: Mapped[List["PokemonAbilityLink"]] = relationship(back_populates="pokemon", cascade="save-update",
                                                               primaryjoin="Pokemon.id == foreign(PokemonAbilityLink.pokemon_key)")

    forms: Mapped[List["PokemonForm"]] = relationship(back_populates="pokemon", cascade="save-update",
                                            primaryjoin="Pokemon.id == foreign(PokemonForm.pokemon_key)")
    
    game_indices: Mapped[List["PokemonGameIndex"]] = relationship(back_populates="object_ref", cascade="save-update",
                                            primaryjoin="Pokemon.id == foreign(PokemonGameIndex.object_key)")
    
    held_items: Mapped[List["PokemonHeldItem"]] = relationship(back_populates="pokemon", cascade="save-update",
                                            primaryjoin="Pokemon.id == foreign(PokemonHeldItem.pokemon_key)")
    
    encounters: Mapped[List["Encounter"]] = relationship(back_populates="pokemon", cascade="save-update",
                                                         primaryjoin="Pokemon.id == foreign(Encounter.pokemon_key)")
    
    moves: Mapped[List["PokemonMove"]] = relationship(back_populates="pokemon", cascade="save-update",
                                            primaryjoin="Pokemon.id == foreign(PokemonMove.pokemon_key)")
    
 
    evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="pokemon", cascade="save-update",
                                                                      primaryjoin="Pokemon.id == foreign(EvolutionDetail.pokemon_key)")
    
    #sprites # don't need these if we want sprites, can download them from github https://github.com/PokeAPI/sprites#sprites
    #cries # https://github.com/PokeAPI/cries#cries

    _cache: Dict[int, "Pokemon"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Pokemon_PokeApiId"),
    )

    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon.csv", 
                        "relationships": {
                            "species_id": ManyToOneAttrs("species","species_key"),
                        },
                        "merge_csvs": (MergeCSV("pokemon_stats.csv", "pokemon_id", 
                                                rename_columns={"base_stat": "hp", 
                                                                "effort": "hp_ev",
                                                                "stat_id": "stat_id_hp"},
                                                filter=FilterCSV("stat_id", FilterOperation.EQUAL, 1)),
                                        MergeCSV("pokemon_stats.csv", "pokemon_id", 
                                                rename_columns={"base_stat": "attack", 
                                                                "effort": "attack_ev",
                                                                "stat_id": "stat_id_attack"},
                                                filter=FilterCSV("stat_id", FilterOperation.EQUAL, 2)),
                                        MergeCSV("pokemon_stats.csv", "pokemon_id", 
                                                rename_columns={"base_stat": "defense", 
                                                                "effort": "defense_ev",
                                                                "stat_id": "stat_id_defense"},
                                                filter=FilterCSV("stat_id", FilterOperation.EQUAL, 3)),
                                        MergeCSV("pokemon_stats.csv", "pokemon_id", 
                                                rename_columns={"base_stat": "special_attack", 
                                                                "effort": "special_attack_ev",
                                                                "stat_id": "stat_id_special_attack"},
                                                filter=FilterCSV("stat_id", FilterOperation.EQUAL, 4)),
                                        MergeCSV("pokemon_stats.csv", "pokemon_id", 
                                                rename_columns={"base_stat": "special_defense", 
                                                                "effort": "special_defense_ev",
                                                                "stat_id": "stat_id_special_defense"},
                                                filter=FilterCSV("stat_id", FilterOperation.EQUAL, 5)),
                                        MergeCSV("pokemon_stats.csv", "pokemon_id", 
                                                rename_columns={"base_stat": "speed", 
                                                                "effort": "speed_ev",
                                                                "stat_id": "stat_id_speed"},
                                                filter=FilterCSV("stat_id", FilterOperation.EQUAL, 6)),)})
    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["Pokemon"]:
        pkmns = []
        for id_, pkmn_data in df.iterrows():
            poke_api_id = id_
            name = pkmn_data.identifier
            base_experience = pkmn_data.base_experience
            height = pkmn_data.height
            weight = pkmn_data.weight
            is_default = pkmn_data.is_default
            order = pkmn_data.order
            hp = pkmn_data.hp
            hp_ev = pkmn_data.hp_ev
            attack = pkmn_data.attack
            attack_ev = pkmn_data.attack_ev
            defense = pkmn_data.defense
            defense_ev = pkmn_data.defense_ev
            special_attack = pkmn_data.special_attack
            special_attack_ev = pkmn_data.special_attack_ev
            special_defense = pkmn_data.special_defense
            special_defense_ev = pkmn_data.special_defense_ev
            speed = pkmn_data.speed
            speed_ev = pkmn_data.speed_ev
            pkmn = cls(poke_api_id=poke_api_id, name=name, base_experience=base_experience, height=height, weight=weight, is_default=is_default, order=order,
                       hp=hp, hp_ev=hp_ev, attack=attack, attack_ev=attack_ev, defense=defense, defense_ev=defense_ev, special_attack=special_attack,
                       special_attack_ev=special_attack_ev, special_defense=special_defense, special_defense_ev=special_defense_ev, speed=speed, speed_ev=speed_ev)
            cls._cache[pkmn.poke_api_id] = pkmn
            pkmns.append(pkmn)
        return pkmns
    
    def __init__(self, poke_api_id: int, name: str, base_experience: int, height: int, weight: int, is_default: bool, order: int, hp: int, hp_ev: int, attack: int, attack_ev: int,
                 defense: int, defense_ev: int, special_attack: int, special_attack_ev: int, special_defense: int, special_defense_ev: int, speed: int, speed_ev: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.base_experience = base_experience
        self.height = height
        self.weight = weight
        self.is_default = is_default
        self.order = order

        self.hp = hp
        self.hp_ev = hp_ev
        self.attack = attack
        self.attack_ev = attack_ev
        self.defense = defense
        self.defense_ev = defense_ev
        self.special_attack = special_attack
        self.special_attack_ev = special_attack_ev
        self.special_defense = special_defense
        self.special_defense_ev = special_defense_ev
        self.speed = speed
        self.speed_ev = speed_ev

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier
        if self.base_experience != data.base_experience:
            self.base_experience = data.base_experience
        if self.height != data.height:
            self.height = data.height
        if self.weight != data.weight:
            self.weight = data.weight
        if self.is_default != data.is_default:
            self.is_default = data.is_default
        if self.order != data.order:
            self.order = data.order

        if self.hp != data.hp:
            self.hp = data.hp
        if self.hp_ev != data.hp_ev:
            self.hp_ev = data.hp_ev
        if self.attack != data.attack:
            self.attack = data.attack
        if self.attack_ev != data.attack_ev:
            self.attack_ev = data.attack_ev
        if self.defense != data.defense:
            self.defense = data.defense
        if self.defense_ev != data.defense_ev:
            self.defense_ev = data.defense_ev
        if self.special_attack != data.special_attack:
            self.special_attack = data.special_attack
        if self.special_attack_ev != data.special_attack_ev:
            self.special_attack_ev = data.special_attack_ev
        if self.special_defense != data.special_defense:
            self.special_defense = data.special_defense
        if self.special_defense_ev != data.special_defense_ev:
            self.special_defense_ev = data.special_defense_ev
        if self.speed != data.speed:
            self.speed = data.speed
        if self.speed_ev != data.speed_ev:
            self.speed_ev = data.speed_ev

class PokemonAbilityLink(Base, CSVResource):
    __tablename__ = "PokemonAbilityLink"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    pokemon_key: Mapped[int] = mapped_column(Integer)
    ability_key: Mapped[int] = mapped_column(Integer)
    generation_key: Mapped[Optional[int]] = mapped_column(Integer)
    is_hidden: Mapped[bool] = mapped_column(Boolean)
    slot: Mapped[int] = mapped_column(TinyInteger)

    pokemon: Mapped["Pokemon"] = relationship(back_populates="ability_slots", cascade="save-update",
                                              primaryjoin="Pokemon.id == PokemonAbilityLink.pokemon_key",
                                              foreign_keys=pokemon_key)
    
    ability: Mapped["PokemonAbility"] = relationship(back_populates="pokemon_slots", cascade="save-update",
                                              primaryjoin="PokemonAbility.id == PokemonAbilityLink.ability_key",
                                              foreign_keys=ability_key)
    
    generation: Mapped["Generation"] = relationship(cascade="save-update",
                                              primaryjoin="Generation.id == PokemonAbilityLink.generation_key",
                                              foreign_keys=generation_key)

    table_args__ = (
        UniqueConstraint("pokemon_key","ability_key","generation_key",name="ux_PokemonAbilityLink_PokeAbilityGen"),
    )
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_abilities.csv", 
                         "concat_csvs": ("pokemon_abilities_past.csv",),
                         "relationships": {
                             "pokemon_id": ManyToOneAttrs("pokemon","pokemon_key"),
                             "ability_id": ManyToOneAttrs("ability","ability_key"),
                             "generation_id": ManyToOneAttrs("generation", "generation_key")
                         },
                         "append_unique_attrs":("slot",)})
    
    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.is_hidden = data.is_hidden
        self.slot = data.slot

    def compare(self, data: pd.Series):
        if self.is_hidden != data.is_hidden:
            self.is_hidden = data.is_hidden
        if self.slot != data.slot:
            self.slot = data.slot

    def get_unique_key(self):
        gen_id = self.generation.poke_api_id if self.generation else None
        # Some (only sv) pokemon have the same ability in slots 1 and 3
        # so the combination of pokemon/ability is not unique
        # Need to also add in slot
        return  str(self.slot)+ ":" + str(self.pokemon.poke_api_id) + ":" + str(self.ability.poke_api_id) + ":" + str(gen_id)


class AbstractTypeLink(Base, CSVResource):
    __tablename__ = "PokemonTypeLink"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    type_key: Mapped[int] = mapped_column(Integer)
    slot: Mapped[int] = mapped_column(TinyInteger)
    object_type: Mapped[str] = mapped_column(String(20))
    object_key: Mapped[int] = mapped_column(Integer)

    __mapper_args__ = {
        "polymorphic_on": "object_type",
        "polymorphic_abstract": True
    }

    
    type_: Mapped["PokemonType"] = relationship(back_populates="pokemon_slots", cascade="save-update",
                                              primaryjoin="PokemonType.id == AbstractTypeLink.type_key",
                                              foreign_keys=type_key)

    table_args__ = (
        UniqueConstraint("object_key","type_key","object_type",name="ux_PokemonTypeLink_PokeType"),
    )
    relationship_attr_map = {"type_id": ManyToOneAttrs("type_","type_key")}
    
    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.slot = data.slot

    def compare(self, data: pd.Series):
        if self.slot != data.slot:
            self.slot = data.slot

    def get_unique_key(self):
        return str(self.type_.poke_api_id)
    
class AbstractPokemonTypeLink(AbstractTypeLink):
    
    relationship_attr_map = dict(AbstractTypeLink.relationship_attr_map)
    relationship_attr_map.update({"pokemon_id": ManyToOneAttrs("pokemon","object_key")})

    pokemon: Mapped["Pokemon"] = relationship(back_populates="type_slots", cascade="save-update",
                                              primaryjoin="Pokemon.id == AbstractPokemonTypeLink.object_key",
                                              foreign_keys="AbstractTypeLink.object_key")
    
    __mapper_args__ = {
        "polymorphic_abstract": True
    }

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.pokemon.poke_api_id)

class PokemonTypeLink(AbstractPokemonTypeLink):
    relationship_attr_map = dict(AbstractPokemonTypeLink.relationship_attr_map)
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_types.csv", "relationships": relationship_attr_map})
    
    __mapper_args__ = {"polymorphic_identity": "Pokemon"}
    
    def get_unique_key(self):
        return super().get_unique_key()

    
class PokemonPastTypeLink(AbstractPokemonTypeLink):
    generation_key: Mapped[Optional[int]] = mapped_column(Integer)

    relationship_attr_map = dict(AbstractPokemonTypeLink.relationship_attr_map)
    relationship_attr_map.update({"generation_id": ManyToOneAttrs("generation", "generation_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_types_past.csv", "relationships": relationship_attr_map})

    generation: Mapped["Generation"] = relationship(cascade="save-update",
                                              primaryjoin="Generation.id == PokemonPastTypeLink.generation_key",
                                              foreign_keys=generation_key)
    
    __mapper_args__ = {"polymorphic_identity": "PokemonPast"}

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.generation.poke_api_id)
    
class PokemonFormTypeLink(AbstractTypeLink):
    relationship_attr_map = dict(AbstractTypeLink.relationship_attr_map)
    relationship_attr_map.update({"pokemon_form_id": ManyToOneAttrs("form","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_form_types.csv", "relationships": relationship_attr_map})

    form: Mapped["PokemonForm"] = relationship(back_populates="type_slots", cascade="save-update",
                                              primaryjoin="PokemonForm.id == PokemonFormTypeLink.object_key",
                                              foreign_keys="AbstractTypeLink.object_key")
    
    __mapper_args__ = {"polymorphic_identity": "PokemonForm"}

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.form.poke_api_id)

class PokemonHeldItem(Base, CSVResource):
    __tablename__ = "PokemonHeldItem"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    pokemon_key: Mapped[int] = mapped_column(Integer)
    item_key: Mapped[int] = mapped_column(Integer)
    version_key: Mapped[int] = mapped_column(Integer)
    rarity: Mapped[int] = mapped_column(Integer)

    item: Mapped["Item"] = relationship(back_populates="held_by_pokemon", cascade="save-update",
                                        primaryjoin="Item.id == PokemonHeldItem.item_key",
                                        foreign_keys=item_key)
    
    version: Mapped["Version"] = relationship(primaryjoin="Version.id == PokemonHeldItem.version_key",
                                            foreign_keys=version_key, cascade="save-update")
    
    pokemon: Mapped["Pokemon"] = relationship(back_populates="held_items", cascade="save-update",
                                            primaryjoin="Pokemon.id == PokemonHeldItem.pokemon_key",
                                            foreign_keys=pokemon_key)
    
    table_args__ = (
        UniqueConstraint("pokemon_key","item_key","version_key",name="ux_PokemonHeldItem_PkmnItemVersion"),
    )
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_items.csv", 
                                   "relationships": {"pokemon_id": ManyToOneAttrs("pokemon", "pokemon_key"),
                                                     "version_id": ManyToOneAttrs("version", "version_key"),
                                                     "item_id": ManyToOneAttrs("item", "item_key")}})

    
    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.rarity = data.rarity

    def compare(self, data: pd.Series):
        if self.rarity != data.rarity:
            self.rarity = data.rarity

    def get_unique_key(self):
        return str(self.pokemon.poke_api_id) + ":" + str(self.version.poke_api_id) + ":" + str(self.item.poke_api_id)

class PokemonMove(Base, CSVResource):
    __tablename__ = "PokemonMove"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    move_key: Mapped[int] = mapped_column(Integer)
    pokemon_key: Mapped[int] = mapped_column(Integer)
    version_group_key: Mapped[int] = mapped_column(Integer)
    move_learn_method_key: Mapped[int] = mapped_column(Integer)
    level_learned_at: Mapped[int] = mapped_column(Integer)
    order: Mapped[Optional[int]] = mapped_column(Integer)

    move: Mapped["Move"] = relationship(back_populates="learned_by_pokemon", cascade="save-update",
                                            primaryjoin="Move.id == PokemonMove.move_key",
                                            foreign_keys=move_key)

    version_group: Mapped["VersionGroup"] = relationship(primaryjoin="VersionGroup.id == PokemonMove.version_group_key",
                                            foreign_keys=version_group_key, cascade="save-update")
    
    move_learn_method: Mapped["MoveLearnMethod"] = relationship(back_populates="pokemon_moves", cascade="save-update",
                                            primaryjoin="MoveLearnMethod.id == PokemonMove.move_learn_method_key",
                                            foreign_keys=move_learn_method_key)

    pokemon: Mapped["Pokemon"] = relationship(back_populates="moves", cascade="save-update",
                                            primaryjoin="Pokemon.id == PokemonMove.pokemon_key",
                                            foreign_keys=pokemon_key)
    
    table_args__ = (
        UniqueConstraint("pokemon_key","move_key","version_group_key", "move_learn_method_key",name="ux_PokemonMove_PkmnMoveVGMethod"),
    )
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_moves.csv", 
                                   "relationships": {"pokemon_id": ManyToOneAttrs("pokemon", "pokemon_key"),
                                                     "version_group_id": ManyToOneAttrs("version_group", "version_group_key"),
                                                     "move_id": ManyToOneAttrs("move", "move_key"),
                                                     "pokemon_move_method_id": ManyToOneAttrs("move_learn_method", "move_learn_method_key")},
                                    "append_unique_attrs":("level",)})
    
    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.level_learned_at = data.level
        self.order = data.order

    def compare(self, data: pd.Series):
        if self.level_learned_at != data.level:
            self.level_learned_at = data.level
        if self.order != data.order:
            self.order = data.order

    def get_unique_key(self):
        return  str(self.level_learned_at)+ ":" + str(self.pokemon.poke_api_id) + ":" + str(self.version_group.poke_api_id) + ":" + str(self.move.poke_api_id) + ":" + str(self.move_learn_method.poke_api_id)

class PokemonColor(Base, PokeApiResource):
    __tablename__ = "PokemonColor"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    names: Mapped[List["PokemonColorName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                            primaryjoin="PokemonColor.id == foreign(PokemonColorName.object_key)")
    
    pokemon_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="color", cascade="save-update",
                                            primaryjoin="PokemonColor.id == foreign(PokemonSpecies.color_key)")
    
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonColor_PokeApiId"),
    )
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_colors.csv", 
                         "relationships": {}})
    _cache: Dict[int, "PokemonColor"] = {}

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonColor"]:
        colors = []
        for id_, color_data in df.iterrows():
            poke_api_id = id_
            name = color_data.identifier
            color = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[color.poke_api_id] = color
            colors.append(color)
        return colors
    
    def __init__(self, poke_api_id: int, name: str,):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

class PokemonForm(Base, PokeApiResource):
    __tablename__ = "PokemonForm"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    pokemon_key: Mapped[int] = mapped_column(Integer)
    order: Mapped[int] = mapped_column(Integer)
    form_order: Mapped[int] = mapped_column(Integer)
    is_default: Mapped[bool] = mapped_column(Boolean)
    is_battle_only: Mapped[bool] = mapped_column(Boolean)
    is_mega: Mapped[bool] = mapped_column(Boolean)
    form_name: Mapped[Optional[str]] = mapped_column(String(100))
    version_group_key: Mapped[int] = mapped_column(Integer)

    pokemon: Mapped["Pokemon"] = relationship(back_populates="forms", cascade="save-update",
                                            primaryjoin="PokemonForm.pokemon_key == Pokemon.id",
                                            foreign_keys=pokemon_key)
    
    type_slots: Mapped[List["PokemonFormTypeLink"]] = relationship(back_populates="form", cascade="save-update",
                                                                   primaryjoin="PokemonForm.id == foreign(PokemonFormTypeLink.object_key)")


    #sprites # don't need these if we want sprites, can download them from github https://github.com/PokeAPI/sprites#sprites
    version_group: Mapped["VersionGroup"] = relationship(primaryjoin="PokemonForm.version_group_key == VersionGroup.id",
                                            foreign_keys=version_group_key, cascade="save-update")
    
    game_indices: Mapped[List["FormGameIndex"]] =  relationship(back_populates="object_ref", cascade="save-update",
                                                          primaryjoin="PokemonForm.id == foreign(FormGameIndex.object_key)")
    
    pokeathlon_stats: Mapped[List["PokemonFormPokeathlonStat"]] = relationship(back_populates="form", cascade="save-update",
                                                                               primaryjoin="PokemonForm.id == foreign(PokemonFormPokeathlonStat.pokemon_form_key)")
    
    names: Mapped[List["PokemonFormName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                          primaryjoin="PokemonForm.id == foreign(PokemonFormName.object_key)")
    
    form_names: Mapped[List["PokemonFormFormName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                          primaryjoin="PokemonForm.id == foreign(PokemonFormFormName.object_key)")
    
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonForm_PokeApiId"),
    )
    
    _cache: Dict[int, "PokemonForm"] = {}

    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_forms.csv", 
                         "relationships": {
                             "pokemon_id": ManyToOneAttrs("pokemon","pokemon_key"),
                             "introduced_in_version_group_id": ManyToOneAttrs("version_group","version_group_key")
                         }})
    
    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonForm"]:
        forms = []
        for id_, form_data in df.iterrows():
            poke_api_id = id_
            name = form_data.identifier
            form_name = form_data.form_identifier
            order = form_data.order
            form_order = form_data.form_order
            is_default = form_data.is_default
            is_battle_only = form_data.is_battle_only
            is_mega = form_data.is_mega
            form = cls(poke_api_id=poke_api_id, name=name, form_name=form_name, order=order, form_order=form_order, is_default=is_default, is_battle_only=is_battle_only, is_mega=is_mega)
            cls._cache[form.poke_api_id] = form
            forms.append(form)
        return forms
    
    
    def __init__(self, poke_api_id: int, name: str, form_name: str, order: int, form_order: int, is_default: bool, is_battle_only: bool, is_mega: bool):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.form_name = form_name
        self.order = order
        self.form_order = form_order
        self.is_default = is_default
        self.is_battle_only = is_battle_only
        self.is_mega = is_mega

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier
        if self.form_name != data.form_identifier:
            self.form_name = data.form_identifier
        if self.order != data.order:
            self.order = data.order
        if self.form_order != data.form_order:
            self.form_order = data.form_order
        if self.is_default != data.is_default:
            self.is_default = data.is_default
        if self.is_battle_only != data.is_battle_only:
            self.is_battle_only = data.is_battle_only
        if self.is_mega != data.is_mega:
            self.is_mega = data.is_mega

class PokemonFormPokeathlonStat(Base, CSVResource):
    __tablename__ = "PokemonFormPokeathlonStat"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    minimum_stat: Mapped[int] = mapped_column(TinyInteger)
    base_stat: Mapped[int] = mapped_column(TinyInteger)
    maximum_stat: Mapped[int] = mapped_column(TinyInteger)
    pokemon_form_key: Mapped[int] = mapped_column(Integer)
    pokeathlon_stat_key: Mapped[int] = mapped_column(Integer)

    form: Mapped["PokemonForm"] = relationship(back_populates="pokeathlon_stats", cascade="save-update",
                                               primaryjoin="PokemonFormPokeathlonStat.pokemon_form_key == PokemonForm.id",
                                               foreign_keys=pokemon_form_key)
    pokeathlon_stat: Mapped["PokeathlonStat"] = relationship(cascade="save-update",
                                                             primaryjoin="PokemonFormPokeathlonStat.pokeathlon_stat_key == PokeathlonStat.id",
                                                             foreign_keys=pokeathlon_stat_key)
    
    table_args__ = (
        UniqueConstraint("pokemon_form_key","pokeathlon_stat_key",name="ux_PokemonFormPokeathlonStat_FormStat"),
    )
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_form_pokeathlon_stats.csv", 
                         "relationships": {
                             "pokemon_form_id": ManyToOneAttrs("form","pokemon_form_key"),
                             "pokeathlon_stat_id": ManyToOneAttrs("pokeathlon_stat","pokeathlon_stat_key")
                         }})
    
    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.minimum_stat = data.minimum_stat
        self.base_stat = data.base_stat
        self.maximum_stat = data.maximum_stat

    def compare(self, data: pd.Series):
        if self.minimum_stat != data.minimum_stat:
            self.minimum_stat = data.minimum_stat
        if self.base_stat != data.base_stat:
            self.base_stat = data.base_stat
        if self.maximum_stat != data.maximum_stat:
            self.maximum_stat = data.maximum_stat

    def get_unique_key(self):
        return str(self.form.poke_api_id) + ":" + str(self.pokeathlon_stat.poke_api_id)

class PokemonHabitat(Base, PokeApiResource):
    __tablename__ = "PokemonHabitat"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    names: Mapped[List["PokemonHabitatName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                          primaryjoin="PokemonHabitat.id == foreign(PokemonHabitatName.object_key)")
    
    pokemon_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="habitat", cascade="save-update",
                                                          primaryjoin="PokemonHabitat.id == foreign(PokemonSpecies.habitat_key)")

    _cache: Dict[int, "PokemonHabitat"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_habitats.csv", 
                         "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonHabitat_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonHabitat"]:
        habitats = []
        for id_, habitat_data in df.iterrows():
            poke_api_id = id_
            name = habitat_data.identifier
            habitat = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[habitat.poke_api_id] = habitat
            habitats.append(habitat)
        return habitats
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

class PokemonShape(Base, PokeApiResource):
    __tablename__ = "PokemonShape"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    awesome_names: Mapped[List["PokemonShapeAwesomeName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                          primaryjoin="PokemonShape.id == foreign(PokemonShapeAwesomeName.object_key)")
    
    names: Mapped[List["PokemonShapeName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                          primaryjoin="PokemonShape.id == foreign(PokemonShapeName.object_key)")
    
    descriptions: Mapped[List["PokemonShapeDescription"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                          primaryjoin="PokemonShape.id == foreign(PokemonShapeDescription.object_key)")
    
    pokemon_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="shape", cascade="save-update",
                                                          primaryjoin="PokemonShape.id == foreign(PokemonSpecies.shape_key)")
    
    _cache: Dict[int, "PokemonShape"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_shapes.csv", 
                         "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonShape_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonShape"]:
        shapes = []
        for id_, shape_data in df.iterrows():
            poke_api_id = id_
            name = shape_data.identifier
            shape = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[shape.poke_api_id] = shape
            shapes.append(shape)
        return shapes
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

class PokemonSpecies(Base, PokeApiResource):
    __tablename__ = "PokemonSpecies"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(Integer)
    gender_rate: Mapped[int] = mapped_column(TinyInteger)
    capture_rate: Mapped[int] = mapped_column(SmallInteger)
    base_happiness: Mapped[Optional[int]] = mapped_column(SmallInteger)
    is_baby: Mapped[bool] = mapped_column(Boolean)
    is_legendary: Mapped[bool] = mapped_column(Boolean)
    is_mythical: Mapped[bool] = mapped_column(Boolean)
    hatch_counter: Mapped[Optional[int]] = mapped_column(TinyInteger)
    has_gender_differences: Mapped[bool] = mapped_column(Boolean)
    forms_switchable: Mapped[bool] = mapped_column(Boolean)
    conquest_order: Mapped[Optional[int]] = mapped_column(SmallInteger)

    generation_key: Mapped[int] = mapped_column(Integer)
    evolves_from_species_key: Mapped[Optional[int]] = mapped_column(Integer)
    evolution_chain_key: Mapped[int] = mapped_column(Integer)
    color_key: Mapped[int] = mapped_column(Integer)
    shape_key: Mapped[Optional[int]] = mapped_column(Integer)
    habitat_key: Mapped[Optional[int]] = mapped_column(Integer)
    growth_rate_key: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonSpecies_PokeApiId"),
        UniqueConstraint("name",name="ux_PokemonSpecies_name"),
    )

    generation: Mapped["Generation"] = relationship(back_populates="pokemon_species", cascade="save-update",
                                            primaryjoin="Generation.id == PokemonSpecies.generation_key",
                                            foreign_keys=generation_key)
    
    evolves_from_species: Mapped["PokemonSpecies"] = relationship(back_populates="evolves_to_species", remote_side=id, cascade="save-update",
                                                                  primaryjoin="PokemonSpecies.id == PokemonSpecies.evolves_from_species_key",
                                                                  foreign_keys=evolves_from_species_key)

    evolution_chain: Mapped["EvolutionChain"] = relationship(#back_populates="species", 
                                            cascade="save-update",
                                            primaryjoin="EvolutionChain.id == PokemonSpecies.evolution_chain_key",
                                            foreign_keys=evolution_chain_key)

    color: Mapped["PokemonColor"] = relationship(back_populates="pokemon_species", cascade="save-update",
                                            primaryjoin="PokemonColor.id == PokemonSpecies.color_key",
                                            foreign_keys=color_key)
    
    shape: Mapped["PokemonShape"] = relationship(back_populates="pokemon_species", cascade="save-update",
                                            primaryjoin="PokemonShape.id == PokemonSpecies.shape_key",
                                            foreign_keys=shape_key)
    
    habitat: Mapped["PokemonHabitat"] = relationship(back_populates="pokemon_species", cascade="save-update",
                                                     primaryjoin="PokemonHabitat.id == PokemonSpecies.habitat_key",
                                                     foreign_keys=habitat_key)

    growth_rate: Mapped["GrowthRate"] = relationship(back_populates="pokemon_species", cascade="save-update",
                                            primaryjoin="GrowthRate.id == PokemonSpecies.growth_rate_key",
                                            foreign_keys=growth_rate_key)
    
    egg_groups: Mapped[List["EggGroup"]] = relationship(back_populates="species", secondary=SpeciesToEggGroupLink, cascade="save-update")
    

    varieties: Mapped[List["Pokemon"]] = relationship(back_populates="species", cascade="save-update", order_by="Pokemon.order",
                                                    primaryjoin="PokemonSpecies.id == foreign(Pokemon.species_key)")

    pokedex_entries: Mapped[List["PokedexEntry"]] = relationship(back_populates="pokemon_species", cascade="save-update",
                                                    primaryjoin="PokemonSpecies.id == foreign(PokedexEntry.pokemon_species_key)")
    
    
    evolves_to_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="evolves_from_species", cascade="save-update",
                                                                      primaryjoin="PokemonSpecies.id == foreign(PokemonSpecies.evolves_from_species_key)")
    
    evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="evolved_species", cascade="save-update",
                                                             primaryjoin="foreign(EvolutionDetail.evolved_species_key) == PokemonSpecies.id")
    
    party_evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="party_species", cascade="save-update",
                                                                            primaryjoin="PokemonSpecies.id == foreign(EvolutionDetail.party_species_key)")
    
    trade_evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="trade_species", cascade="save-update",
                                                                            primaryjoin="PokemonSpecies.id == foreign(EvolutionDetail.trade_species_key)")
    
    pal_park_encounters: Mapped[List["PalParkEncounter"]] = relationship(back_populates="pokemon_species", cascade="save-update",
                                                                         primaryjoin="PokemonSpecies.id == foreign(PalParkEncounter.pokemon_species_key)")
    
    names: Mapped[List["PokemonName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="PokemonSpecies.id == foreign(PokemonName.object_key)")
    flavor_text_entries: Mapped[List["PokemonSpeciesFlavorText"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="PokemonSpecies.id == foreign(PokemonSpeciesFlavorText.object_key)")
    form_descriptions: Mapped[List["PokemonFormDescription"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="PokemonSpecies.id == foreign(PokemonFormDescription.object_key)")
    genera: Mapped[List["PokemonGenus"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                      primaryjoin="PokemonSpecies.id == foreign(PokemonGenus.object_key)")
    
    _cache: Dict[int, "PokemonSpecies"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_species.csv",
                                   "merge_csvs": (MergeCSV("pokemon_egg_groups.csv", "species_id"),),
                                   "group_by": GroupByCSV(['egg_group_id'], ['id','identifier','generation_id','evolves_from_species_id','evolution_chain_id','color_id','shape_id','habitat_id','gender_rate','capture_rate','base_happiness','is_baby','hatch_counter','has_gender_differences','growth_rate_id','forms_switchable','is_legendary','is_mythical','order','conquest_order']),
                          "relationships": {"generation_id": ManyToOneAttrs("generation","generation_key"),
                                            "evolves_from_species_id": ManyToOneAttrs("evolves_from_species","evolves_from_species_key"),
                                            "evolution_chain_id": ManyToOneAttrs("evolution_chain","evolution_chain_key"),
                                            "color_id": ManyToOneAttrs("color","color_key"),
                                            "shape_id": ManyToOneAttrs("shape", "shape_key"),
                                            "habitat_id": ManyToOneAttrs("habitat","habitat_key"),
                                            "growth_rate_id": ManyToOneAttrs("growth_rate", "growth_rate_key"),
                                            "egg_group_id": ManyToManyAttr("egg_groups")}})
    

    
    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonSpecies"]:
        speciess = []
        for id_, species_data in df.iterrows():
            poke_api_id = id_
            name = species_data.identifier
            order = species_data.order
            gender_rate = species_data.gender_rate
            capture_rate = species_data.capture_rate
            base_happiness = species_data.base_happiness
            is_baby = species_data.is_baby
            is_legendary = species_data.is_legendary
            is_mythical = species_data.is_mythical
            hatch_counter = species_data.hatch_counter
            has_gender_differences = species_data.has_gender_differences
            forms_switchable = species_data.forms_switchable
            conquest_order = species_data.conquest_order
            species = cls(poke_api_id=poke_api_id, name=name, order=order, gender_rate=gender_rate, capture_rate=capture_rate, base_happiness=base_happiness, is_baby=is_baby,
                      is_legendary=is_legendary, is_mythical=is_mythical, hatch_counter=hatch_counter, has_gender_differences=has_gender_differences, forms_switchable=forms_switchable,
                      conquest_order=conquest_order)
            cls._cache[species.poke_api_id] = species
            speciess.append(species)
        return speciess
    
    def __init__(self, poke_api_id: int, name: str, order: int, gender_rate: int, capture_rate: int, base_happiness: int, is_baby: bool,
                      is_legendary: bool, is_mythical: bool, hatch_counter: int, has_gender_differences: bool, forms_switchable: bool, conquest_order: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.order = order
        self.gender_rate = gender_rate
        self.capture_rate = capture_rate
        self.base_happiness = base_happiness
        self.is_baby = is_baby
        self.is_legendary = is_legendary
        self.is_mythical = is_mythical
        self.hatch_counter = hatch_counter
        self.has_gender_differences = has_gender_differences
        self.forms_switchable = forms_switchable
        self.conquest_order = conquest_order

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier
        if self.order != data.order:
            self.order = data.order
        if self.gender_rate != data.gender_rate:
            self.gender_rate = data.gender_rate
        if self.capture_rate != data.capture_rate:
            self.capture_rate = data.capture_rate
        if self.base_happiness != data.base_happiness:
            self.base_happiness = data.base_happiness
        if self.is_baby != data.is_baby:
            self.is_baby = data.is_baby
        if self.is_legendary != data.is_legendary:
            self.is_legendary = data.is_legendary
        if self.is_mythical != data.is_mythical:
            self.is_mythical = data.is_mythical
        if self.hatch_counter != data.hatch_counter:
            self.hatch_counter = data.hatch_counter
        if self.has_gender_differences != data.has_gender_differences:
            self.has_gender_differences = data.has_gender_differences
        if self.forms_switchable != data.forms_switchable:
            self.forms_switchable = data.forms_switchable
        if self.conquest_order != data.conquest_order:
            self.conquest_order = data.conquest_order



# Stats
class PokemonStat(Base, PokeApiResource):
    __tablename__ = "PokemonStat"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    game_index: Mapped[Optional[int]] = mapped_column(TinyInteger)
    is_battle_only: Mapped[Optional[bool]] = mapped_column(Boolean)
    damage_class_key: Mapped[Optional[int]] = mapped_column(Integer)

    changing_moves: Mapped[List["MoveStatChange"]] = relationship(back_populates="stat", cascade="save-update",
                                                                   primaryjoin="PokemonStat.id == foreign(MoveStatChange.stat_key)") 
    
    decreasing_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="decreased_stat", cascade="save-update",
                                                              primaryjoin="PokemonStat.id == foreign(PokemonNature.decreased_stat_key)")
    increasing_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="increased_stat", cascade="save-update",
                                                              primaryjoin="PokemonStat.id == foreign(PokemonNature.increased_stat_key)")

    characteristics: Mapped[List["PokemonCharacteristic"]] = relationship(back_populates="highest_stat", cascade="save-update",
                                                              primaryjoin="PokemonStat.id == foreign(PokemonCharacteristic.highest_stat_key)")

    damage_class: Mapped["DamageClass"] = relationship(primaryjoin="PokemonStat.damage_class_key == DamageClass.id",
                                                       foreign_keys=damage_class_key, cascade="save-update")

    names: Mapped[List["PokemonStatName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                          primaryjoin="PokemonStat.id == foreign(PokemonStatName.object_key)")
    
    _cache: Dict[int, "PokemonStat"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "stats.csv", 
                         "relationships": {
                             "damage_class_id": ManyToOneAttrs("damage_class","damage_class_key")
                         }})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonStat_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonStat"]:
        stats = []
        for id_, stat_data in df.iterrows():
            poke_api_id = id_
            name = stat_data.identifier
            game_index = stat_data.game_index
            is_battle_only = stat_data.is_battle_only
            stat = cls(poke_api_id=poke_api_id, name=name,game_index=game_index, is_battle_only=is_battle_only)
            cls._cache[stat.poke_api_id] = stat
            stats.append(stat)
        return stats
    
    def __init__(self, poke_api_id: int, name: str, game_index: int, is_battle_only: bool):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.game_index = game_index
        self.is_battle_only = is_battle_only

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name
        if self.game_index != data.game_index:
            self.game_index = data.game_index
        if self.is_battle_only != data.is_battle_only:
            self.is_battle_only = data.is_battle_only

# Types
class PokemonType(Base, PokeApiResource): 
    __tablename__ = "PokemonType"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    generation_introduced_key: Mapped[int] = mapped_column(Integer)
    damage_class_key: Mapped[Optional[int]] = mapped_column(Integer)

    generation_introduced: Mapped["Generation"] = relationship(back_populates="types_introduced", cascade="save-update",
                                                               primaryjoin="PokemonType.generation_introduced_key == Generation.id",
                                                               foreign_keys=generation_introduced_key)
    damage_class: Mapped["DamageClass"] = relationship(back_populates="types", cascade="save-update",
                                                       primaryjoin="PokemonType.damage_class_key == DamageClass.id",
                                                       foreign_keys=damage_class_key)

    offensive_relations: Mapped[List["PokemonTypeRelation"]] = relationship(back_populates="offensive_type", cascade="save-update",
                                                                            primaryjoin="PokemonType.id == foreign(PokemonTypeRelation.offensive_type_key)")
    defensive_relations: Mapped[List["PokemonTypeRelation"]] = relationship(back_populates="defensive_type", cascade="save-update",
                                                                            primaryjoin="PokemonType.id == foreign(PokemonTypeRelation.defensive_type_key)")

    pokemon_slots: Mapped[List["AbstractTypeLink"]] = relationship(back_populates="type_", cascade="save-update",
                                                                  primaryjoin="PokemonType.id == foreign(AbstractTypeLink.type_key)")
    moves: Mapped[List["Move"]] = relationship(back_populates="move_type", cascade="save-update",
                                               primaryjoin="PokemonType.id == foreign(Move.move_type_key)")
    
    move_type_evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="known_move_type", cascade="save-update",
                                                                                primaryjoin="PokemonType.id == foreign(EvolutionDetail.known_move_type_key)")
    
    party_evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="party_type", cascade="save-update",
                                                                                primaryjoin="PokemonType.id == foreign(EvolutionDetail.party_type_key)")

    game_indices: Mapped[List["TypeGameIndex"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                               primaryjoin="PokemonType.id == foreign(TypeGameIndex.object_key)")
    
    names: Mapped[List["PokemonTypeName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                          primaryjoin="PokemonType.id == foreign(PokemonTypeName.object_key)")
    
    _cache: Dict[int, "PokemonType"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "types.csv", 
                         "relationships": {
                             "generation_id": ManyToOneAttrs("generation_introduced","generation_introduced_key"),
                             "damage_class_id": ManyToOneAttrs("damage_class","damage_class_key")
                         }})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonType_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonType"]:
        types_ = []
        for id_, type_data in df.iterrows():
            poke_api_id = id_
            name = type_data.identifier
            type_ = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[type_.poke_api_id] = type_
            types_.append(type_)
        return types_
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier



class PokemonTypeRelation(Base, CSVResource):
    __tablename__ = "PokemonTypeRelation"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    offensive_type_key: Mapped[int] = mapped_column(Integer)
    defensive_type_key: Mapped[int] = mapped_column(Integer)
    generation_key: Mapped[Optional[int]] = mapped_column(Integer)
    damage_factor: Mapped[int] = mapped_column(SmallInteger)

    offensive_type: Mapped["PokemonType"] = relationship(back_populates="offensive_relations", cascade="save-update",
                                                         primaryjoin="PokemonTypeRelation.offensive_type_key == PokemonType.id",
                                                         foreign_keys=offensive_type_key)
    defensive_type: Mapped["PokemonType"] = relationship(back_populates="defensive_relations", cascade="save-update",
                                                         primaryjoin="PokemonTypeRelation.defensive_type_key == PokemonType.id",
                                                         foreign_keys=defensive_type_key)
    generation: Mapped["Generation"] = relationship(primaryjoin="PokemonTypeRelation.generation_key == Generation.id",
                                                    foreign_keys=generation_key, cascade="save-update")

    __table_args__ = (
        UniqueConstraint("offensive_type_key","defensive_type_key","generation_key",name="ux_PokemonTypeRelation_offdefgen"),
    )
    csv_data: CSVData = CSVData(**{"primary_csv": "type_efficacy.csv", 
                         "concat_csvs": ("type_efficacy_past.csv",),
                         "relationships": {
                             "damage_type_id": ManyToOneAttrs("offensive_type","offensive_type_key"),
                             "target_type_id": ManyToOneAttrs("defensive_type","defensive_type_key"),
                             "generation_id": ManyToOneAttrs("generation", "generation_key")
                         }})
    
    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.damage_factor = data.damage_factor

    def compare(self, data: pd.Series):
        if self.damage_factor != data.damage_factor:
            self.damage_factor = data.damage_factor

    def get_unique_key(self):
        gen_id = self.generation.poke_api_id if self.generation else None
        return str(self.offensive_type.poke_api_id) + ":" + str(self.defensive_type.poke_api_id) + ":" + str(gen_id)
    
class PokemonGender(Base, PokeApiResource):
    __tablename__ = "PokemonGender"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    _cache: Dict[int, "PokemonGender"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "genders.csv", 
                         "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonGender_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PokemonGender"]:
        genders = []
        for id_, gender_data in df.iterrows():
            poke_api_id = id_
            name = gender_data.identifier
            gender = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[gender.poke_api_id] = gender
            genders.append(gender)
        return genders
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier