from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Computed, UniqueConstraint, Index, Boolean, select

from Base import Base, TinyInteger, Session, get_next_id, PokeApiResource

if TYPE_CHECKING:
    from Berries import BerryFlavor
    from Evolution import EvolutionChain, EvolutionDetail
    from Games import Generation, PokedexEntry, Version, VersionGroup, PokemonGameIndex, TypeGameIndex
    from Items import Item
    from Moves import DamageClass, MoveBattleStyle, Move, MoveLearnMethod, MoveStatChange
    from Locations import PokemonEncounter, PalParkEncounter
    from TextEntries import CharacteristicDescription, AbilityEffect, AbilityEffectChange, AbilityFlavorText
    from TextEntries import PokemonName, PokemonSpeciesFlavorText, PokemonFormDescription, PokemonTypeName
    from TextEntries import PokemonStatName, PokemonNatureName, PokemonAbilityName, EggGroupName
    from TextEntries import GrowthRateDescription, PokemonColorName, PokemonFormName, PokemonFormFormName
    from TextEntries import PokemonHabitatName, PokemonShapeAwesomeName, PokemonShapeName, PokemonGenus

class PokemonAbility(Base):
    __tablename__ = "PokemonAbility"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    generation_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    is_main_series: Mapped[bool] = mapped_column(Boolean)

    generation: Mapped["Generation"] = relationship(back_populates="abilities",
                                            primaryjoin="Generation.id == PokemonAbility.generation_key",
                                            foreign_keys=generation_key)
    
    pokemon_ability_1: Mapped[List["Pokemon"]] = relationship(back_populates="ability_1",
                                                              primaryjoin="PokemonAbility.id == foreign(Pokemon.ability_1_key)")
    pokemon_ability_2: Mapped[List["Pokemon"]] = relationship(back_populates="ability_2",
                                                              primaryjoin="PokemonAbility.id == foreign(Pokemon.ability_2_key)")
    pokemon_hidden_ability: Mapped[List["Pokemon"]] = relationship(back_populates="hidden_ability",
                                                              primaryjoin="PokemonAbility.id == foreign(Pokemon.hidden_ability_key)")

    names: Mapped[List["PokemonAbilityName"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="PokemonAbility.id == foreign(PokemonAbilityName.object_key)")
    effect_entries: Mapped[List["AbilityEffect"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="PokemonAbility.id == foreign(AbilityEffect.object_key)")
    effect_changes: Mapped[List["AbilityEffectChange"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="PokemonAbility.id == foreign(AbilityEffectChange.object_key)")
    flavor_text_entries: Mapped[List["AbilityFlavorText"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="PokemonAbility.id == foreign(AbilityFlavorText.object_key)")

class PokemonCharacteristic(Base):
    __tablename__ = "PokemonCharacteristic"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    highest_stat_key: Mapped[int] = mapped_column(Integer)
    gene_modulo: Mapped[int] = mapped_column(Integer)

    highest_stat: Mapped["PokemonStat"] = relationship(back_populates="characteristics",
                                            primaryjoin="PokemonStat.id == PokemonCharacteristic.highest_stat_key",
                                            foreign_keys=highest_stat_key)
    descriptions: Mapped[List["CharacteristicDescription"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="PokemonCharacteristic.id == foreign(CharacteristicDescription.object_key)")

class EggGroup(Base, PokeApiResource):
    __tablename__ = "EggGroup"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    #poke_api_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EggGroup_PokeApiId"),
    )

    names: Mapped[List["EggGroupName"]] = relationship(back_populates="object_ref",
                                                        primaryjoin="EggGroup.id == foreign(EggGroupName.object_key)")
    species_egg_group_1: Mapped[List["PokemonSpecies"]] = relationship(back_populates="egg_group_1",
                                                        primaryjoin="EggGroup.id == foreign(PokemonSpecies.egg_group_1_key)")
    species_egg_group_2: Mapped[List["PokemonSpecies"]] = relationship(back_populates="egg_group_2",
                                                        primaryjoin="EggGroup.id == foreign(PokemonSpecies.egg_group_2_key)")
    
    _cache: Dict[int, "EggGroup"] = {}

    """ @classmethod
    def get_egg_group(cls, cache_key: int) -> Optional["EggGroup"]:
        if cache_key not in cls._cache:
            with Session() as session:
                egg_group: EggGroup = session.scalars(select(EggGroup).filter_by(poke_api_id=cache_key)).first()
                if egg_group:
                    cls._cache[egg_group.poke_api_id] = egg_group
        return cls._cache.get(cache_key)   """ 
    
    @classmethod
    def parse_data(cls,data) -> "EggGroup":
    #def parse_egg_group(cls,data) -> "EggGroup":
        poke_api_id = data.id_
        name = data.name
        egg_group = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[egg_group.poke_api_id] = egg_group
        return egg_group
    
    def __init__(self, poke_api_id: int, name: str,):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name == data.name

# I don't think this is something I need
# Its not referenced by anything else
'''class GenderEvolution(Base):
    __tablename__ = "GenderEvolution"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    pokemon_species_key: Mapped[int] = mapped_column(Integer)

    pokemon_species: Mapped["PokemonSpecies"] = relationship(back_populates="",
                                            primaryjoin="PokemonSpecies.id == GenderEvolution.pokemon_species_key",
                                            foreign_keys=pokemon_species_key)
'''
class GrowthRate(Base):
    __tablename__ = "GrowthRate"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    formula: Mapped[str] = mapped_column(String(100))

    descriptions: Mapped[List["GrowthRateDescription"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="GrowthRate.id == foreign(GrowthRateDescription.object_key)")
    levels: Mapped[List["GrowthRateExperienceLevel"]] = relationship(back_populates="growth_rate",
                                                              primaryjoin="GrowthRate.id == foreign(GrowthRateExperienceLevel.growth_rate_key)")
    pokemon_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="growth_rate",
                                                              primaryjoin="GrowthRate.id == foreign(PokemonSpecies.growth_rate_key)")

class GrowthRateExperienceLevel(Base):
    __tablename__ = "GrowthRateExperienceLevel"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    growth_rate_key: Mapped[int] = mapped_column(Integer)
    level: Mapped[int] = mapped_column(Integer)
    experience: Mapped[int] = mapped_column(Integer)

    growth_rate: Mapped["GrowthRate"] = relationship(back_populates="levels",
                                            primaryjoin="GrowthRate.id == GrowthRateExperienceLevel.growth_rate_key",
                                            foreign_keys=growth_rate_key)

class PokemonNature(Base):
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

    decreased_stat: Mapped["PokemonStat"] = relationship(back_populates="decreasing_natures",
                                            primaryjoin="PokemonStat.id == PokemonNature.decreased_stat_key",
                                            foreign_keys=decreased_stat_key)
    increased_stat: Mapped["PokemonStat"] = relationship(back_populates="increasing_natures",
                                            primaryjoin="PokemonStat.id == PokemonNature.increased_stat_key",
                                            foreign_keys=increased_stat_key)
    decreased_pokeathlon_stat: Mapped["PokemonStat"] = relationship(back_populates="decreasing_pokeathlon_natures",
                                            primaryjoin="PokemonStat.id == PokemonNature.decreased_pokeathlon_stat_key",
                                            foreign_keys=decreased_pokeathlon_stat_key)
    increased_pokeathlon_stat: Mapped["PokemonStat"] = relationship(back_populates="increasing_pokeathlon_natures",
                                            primaryjoin="PokemonStat.id == PokemonNature.increased_pokeathlon_stat_key",
                                            foreign_keys=increased_pokeathlon_stat_key)
    hates_flavor: Mapped["BerryFlavor"] = relationship(back_populates="hates_natures",
                                            primaryjoin="BerryFlavor.id == PokemonNature.hates_flavor_key",
                                            foreign_keys=hates_flavor_key)
    likes_flavor: Mapped["BerryFlavor"] = relationship(back_populates="likes_natures",
                                            primaryjoin="BerryFlavor.id == PokemonNature.likes_flavor_key",
                                            foreign_keys=likes_flavor_key)

    #pokeathlon_stat_changes # I don't think this is needed, with the stat changes included in this class
    move_battle_style_preferences: Mapped[List["MoveBattleStylePreference"]] = relationship(back_populates="pokemon_nature",
                                                              primaryjoin="PokemonNature.id == foreign(MoveBattleStylePreference.pokemon_nature_key)")

    names: Mapped[List["PokemonNatureName"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="PokemonNature.id == foreign(PokemonNatureName.object_key)")

class MoveBattleStylePreference(Base):
    __tablename__ = "MoveBattleStylePreference"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    move_battle_style_key: Mapped[int] = mapped_column(Integer)
    pokemon_nature_key: Mapped[int] = mapped_column(Integer)
    low_hp_preference: Mapped[int] = mapped_column(Integer)
    high_hp_preference: Mapped[int] = mapped_column(Integer)

    move_battle_style: Mapped["MoveBattleStyle"] = relationship(back_populates="preference",
                                            primaryjoin="MoveBattleStyle.id == MoveBattleStylePreference.move_battle_style_key",
                                            foreign_keys=move_battle_style_key)
    pokemon_nature: Mapped["PokemonNature"] = relationship(back_populates="move_battle_style_preferences",
                                            primaryjoin="PokemonNature.id == MoveBattleStylePreference.pokemon_nature_key",
                                            foreign_keys=pokemon_nature_key)


class Pokemon(Base):
    __tablename__ = "Pokemon"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    species_key: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    base_experience: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    weight: Mapped[int] = mapped_column(Integer)
    is_default: Mapped[bool] = mapped_column(Boolean)
    order: Mapped[int] = mapped_column(Integer)

    type_1_key: Mapped[int] = mapped_column(Integer)
    type_2_key: Mapped[Optional[int]] = mapped_column(Integer)
    ability_1_key: Mapped[int] = mapped_column(Integer)
    ability_2_key: Mapped[Optional[int]] = mapped_column(Integer)
    hidden_ability_key: Mapped[Optional[int]] = mapped_column(Integer)


    hp: Mapped[int] = mapped_column(Integer)
    attack: Mapped[int] = mapped_column(Integer)
    defense: Mapped[int] = mapped_column(Integer)
    special_attack: Mapped[int] = mapped_column(Integer)
    special_defense: Mapped[int] = mapped_column(Integer)
    speed: Mapped[int] = mapped_column(Integer)
    # virtual computed column?
    bst: Mapped[int] = mapped_column(Integer,Computed('hp+attack+defense+special_attack+special_defense+speed',persisted=False))
    
    type_1: Mapped["PokemonType"] = relationship(back_populates="main_types",
                                            primaryjoin="Pokemon.type_1_key == PokemonType.id",
                                            foreign_keys=type_1_key)
    type_2: Mapped["PokemonType"] = relationship(back_populates="secondary_types",
                                            primaryjoin="Pokemon.type_2_key == PokemonType.id",
                                            foreign_keys=type_2_key)
    
    species: Mapped["PokemonSpecies"] = relationship(back_populates="varieties",
                                            primaryjoin="Pokemon.species_key == PokemonSpecies.id",
                                            foreign_keys=species_key)

    ability_1: Mapped["PokemonAbility"] = relationship(back_populates="pokemon_ability_1",
                                            primaryjoin="Pokemon.ability_1_key == PokemonAbility.id",
                                            foreign_keys=ability_1_key)
    ability_2: Mapped["PokemonAbility"] = relationship(back_populates="pokemon_ability_2",
                                            primaryjoin="Pokemon.ability_2_key == PokemonAbility.id",
                                            foreign_keys=ability_2_key)
    hidden_ability: Mapped["PokemonAbility"] = relationship(back_populates="pokemon_hidden_ability",
                                            primaryjoin="Pokemon.hidden_ability_key == PokemonAbility.id",
                                            foreign_keys=hidden_ability_key)

    forms: Mapped[List["PokemonForm"]] = relationship(back_populates="pokemon",
                                            primaryjoin="Pokemon.id == foreign(PokemonForm.pokemon_key)")
    
    game_indices: Mapped[List["PokemonGameIndex"]] = relationship(back_populates="object_ref",
                                            primaryjoin="Pokemon.id == foreign(PokemonGameIndex.object_key)")
    
    held_items: Mapped[List["PokemonHeldItem"]] = relationship(back_populates="pokemon",
                                            primaryjoin="Pokemon.id == foreign(PokemonHeldItem.pokemon_key)")
    
    pokemon_encounters: Mapped[List["PokemonEncounter"]] = relationship(back_populates="pokemon",
                                            primaryjoin="Pokemon.id == foreign(PokemonEncounter.pokemon_key)")
    
    moves: Mapped[List["PokemonMove"]] = relationship(back_populates="pokemon",
                                            primaryjoin="Pokemon.id == foreign(PokemonMove.pokemon_key)")
    
    past_types: Mapped[List["PastTypeLink"]] = relationship(back_populates="pokemon",
                                            primaryjoin="Pokemon.id == foreign(PastTypeLink.pokemon_key)")
    
    evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="pokemon",
                                                                      primaryjoin="Pokemon.id == foreign(EvolutionDetail.pokemon_key)")
    
    #sprites # don't need these if we want sprites, can download them from github https://github.com/PokeAPI/sprites#sprites
    #cries # https://github.com/PokeAPI/cries#cries

class PokemonHeldItem(Base):
    __tablename__ = "PokemonHeldItem"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    pokemon_key: Mapped[int] = mapped_column(Integer)
    item_key: Mapped[int] = mapped_column(Integer)
    version_key: Mapped[int] = mapped_column(Integer)
    rarity: Mapped[int] = mapped_column(Integer)

    item: Mapped["Item"] = relationship(back_populates="held_by_pokemon",
                                        primaryjoin="Item.id == PokemonHeldItem.item_key",
                                        foreign_keys=item_key)
    
    version: Mapped["Version"] = relationship(primaryjoin="Version.id == PokemonHeldItem.version_key",
                                            foreign_keys=version_key)
    
    pokemon: Mapped["Pokemon"] = relationship(back_populates="held_items",
                                            primaryjoin="Pokemon.id == PokemonHeldItem.pokemon_key",
                                            foreign_keys=pokemon_key)


class PokemonMove(Base):
    __tablename__ = "PokemonMove"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    move_key: Mapped[int] = mapped_column(Integer)
    pokemon_key: Mapped[int] = mapped_column(Integer)
    version_group_key: Mapped[int] = mapped_column(Integer)
    move_learn_method_key: Mapped[int] = mapped_column(Integer)
    level_learned_at: Mapped[int] = mapped_column(Integer)

    move: Mapped["Move"] = relationship(back_populates="learned_by_pokemon",
                                            primaryjoin="Move.id == PokemonMove.move_key",
                                            foreign_keys=move_key)

    version_group: Mapped["VersionGroup"] = relationship(primaryjoin="VersionGroup.id == PokemonMove.version_group_key",
                                            foreign_keys=version_group_key)
    
    move_learn_method: Mapped["MoveLearnMethod"] = relationship(back_populates="pokemon_moves",
                                            primaryjoin="MoveLearnMethod.id == PokemonMove.move_learn_method_key",
                                            foreign_keys=move_learn_method_key)

    pokemon: Mapped["Pokemon"] = relationship(back_populates="moves",
                                            primaryjoin="Pokemon.id == PokemonMove.pokemon_key",
                                            foreign_keys=pokemon_key)
    
    """ affecting_stats: Mapped[List["MoveStatAffect"]] = relationship(back_populates="move",
                                                                   primaryjoin="PokemonMove.id == foreign(MoveStatAffect.move_key)") """

class PokemonColor(Base, PokeApiResource):
    __tablename__ = "PokemonColor"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    names: Mapped[List["PokemonColorName"]] = relationship(back_populates="object_ref",
                                            primaryjoin="PokemonColor.id == foreign(PokemonColorName.object_key)")
    
    pokemon_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="color",
                                            primaryjoin="PokemonColor.id == foreign(PokemonSpecies.color_key)")
    
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonColor_PokeApiId"),
    )
    
    _cache: Dict[int, "PokemonColor"] = {}
    
    @classmethod
    def parse_data(cls,data) -> "PokemonColor":
        poke_api_id = data.id_
        name = data.name
        color = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[color.poke_api_id] = color
        return color
    
    def __init__(self, poke_api_id: int, name: str,):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

class PokemonForm(Base):
    __tablename__ = "PokemonForm"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    pokemon_key: Mapped[int] = mapped_column(Integer)
    order: Mapped[int] = mapped_column(Integer)
    form_order: Mapped[int] = mapped_column(Integer)
    is_default: Mapped[bool] = mapped_column(Boolean)
    is_battle_only: Mapped[bool] = mapped_column(Boolean)
    is_mega: Mapped[bool] = mapped_column(Boolean)
    form_name: Mapped[str] = mapped_column(String(100))
    version_group_key: Mapped[int] = mapped_column(Integer)
    type_1_key: Mapped[int] = mapped_column(Integer)
    type_2_key: Mapped[Optional[int]] = mapped_column(Integer)

    pokemon: Mapped["Pokemon"] = relationship(back_populates="forms",
                                            primaryjoin="PokemonForm.pokemon_key == Pokemon.id",
                                            foreign_keys=pokemon_key)
    
    type1: Mapped["PokemonType"] = relationship(primaryjoin="PokemonForm.type_1_key == PokemonType.id",
                                            foreign_keys=type_1_key)
    
    type2: Mapped["PokemonType"] = relationship(primaryjoin="PokemonForm.type_2_key == PokemonType.id",
                                            foreign_keys=type_2_key)
    
    #sprites # don't need these if we want sprites, can download them from github https://github.com/PokeAPI/sprites#sprites
    version_group: Mapped["VersionGroup"] = relationship(primaryjoin="PokemonForm.version_group_key == VersionGroup.id",
                                            foreign_keys=version_group_key)
    
    names: Mapped[List["PokemonFormName"]] = relationship(back_populates="object_ref",
                                                          primaryjoin="PokemonForm.id == foreign(PokemonFormName.object_key)")
    
    form_names: Mapped[List["PokemonFormFormName"]] = relationship(back_populates="object_ref",
                                                          primaryjoin="PokemonForm.id == foreign(PokemonFormFormName.object_key)")

class PokemonHabitat(Base, PokeApiResource):
    __tablename__ = "PokemonHabitat"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    names: Mapped[List["PokemonHabitatName"]] = relationship(back_populates="object_ref",
                                                          primaryjoin="PokemonHabitat.id == foreign(PokemonHabitatName.object_key)")
    
    pokemon_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="habitat",
                                                          primaryjoin="PokemonHabitat.id == foreign(PokemonSpecies.habitat_key)")

    _cache: Dict[int, "PokemonHabitat"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonHabitat_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "PokemonHabitat":
        poke_api_id = data.id_
        name = data.name
        habitat = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[habitat.poke_api_id] = habitat
        return habitat
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

class PokemonShape(Base, PokeApiResource):
    __tablename__ = "PokemonShape"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    awesome_names: Mapped[List["PokemonShapeAwesomeName"]] = relationship(back_populates="object_ref",
                                                          primaryjoin="PokemonShape.id == foreign(PokemonShapeAwesomeName.object_key)")
    
    names: Mapped[List["PokemonShapeName"]] = relationship(back_populates="object_ref",
                                                          primaryjoin="PokemonShape.id == foreign(PokemonShapeName.object_key)")
    
    pokemon_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="shape",
                                                          primaryjoin="PokemonShape.id == foreign(PokemonSpecies.shape_key)")
    
    _cache: Dict[int, "PokemonShape"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_PokemonShape_PokeApiId"),
    )
    
    @classmethod
    def parse_data(cls,data) -> "PokemonShape":
        poke_api_id = data.id_
        name = data.name
        shape = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[shape.poke_api_id] = shape
        return shape
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

class PokemonSpecies(Base, PokeApiResource):
    __tablename__ = "PokemonSpecies"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    #pokeapi_id: Mapped[int] = mapped_column(Integer)
    #national_dex_number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(Integer)
    gender_rate: Mapped[int] = mapped_column(TinyInteger)
    capture_rate: Mapped[int] = mapped_column(TinyInteger)
    base_happinenss: Mapped[int] = mapped_column(TinyInteger)
    is_baby: Mapped[bool] = mapped_column(Boolean)
    is_legendary: Mapped[bool] = mapped_column(Boolean)
    is_mythical: Mapped[bool] = mapped_column(Boolean)
    hatch_counter: Mapped[int] = mapped_column(TinyInteger)
    has_gender_differences: Mapped[bool] = mapped_column(Boolean)
    forms_switchable: Mapped[bool] = mapped_column(Boolean)
    evolves_from_species_key: Mapped[int] = mapped_column(Integer)
    #genus: Mapped[str] = mapped_column(String(100)) # read en from genera
    

    egg_group_1_key: Mapped[int] = mapped_column(Integer)
    egg_group_2_key: Mapped[Optional[int]] = mapped_column(Integer)
    color_key: Mapped[int] = mapped_column(Integer)
    shape_key: Mapped[int] = mapped_column(Integer)
    habitat_key: Mapped[int] = mapped_column(Integer)
    evolution_chain_key: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        #UniqueConstraint("national_dex_number",name="ux_PokemonSpecies_NatDexId"),
        UniqueConstraint("poke_api_id",name="ux_PokemonSpecies_PokeApiId"),
        UniqueConstraint("name",name="ux_PokemonSpecies_name"),
    )

    varieties: Mapped[List["Pokemon"]] = relationship(back_populates="species",
                                                    primaryjoin="PokemonSpecies.id == foreign(Pokemon.species_key)")

    pokedex_entries: Mapped[List["PokedexEntry"]] = relationship(back_populates="pokemon",
                                                    primaryjoin="PokemonSpecies.id == foreign(PokedexEntry.pokemon_species_key)")
    
    evolves_from_species: Mapped["PokemonSpecies"] = relationship(back_populates="evolves_to_species", remote_side=id,
                                                                  primaryjoin="PokemonSpecies.id == PokemonSpecies.evolves_from_species_key",
                                                                  foreign_keys=evolves_from_species_key)
    evolves_to_species: Mapped[List["PokemonSpecies"]] = relationship(back_populates="evolves_from_species",
                                                                      primaryjoin="PokemonSpecies.id == foreign(PokemonSpecies.evolves_from_species_key)")

    growth_rate_key: Mapped[int] = mapped_column(Integer)
    growth_rate: Mapped["GrowthRate"] = relationship(back_populates="pokemon_species",
                                            primaryjoin="GrowthRate.id == PokemonSpecies.growth_rate_key",
                                            foreign_keys=growth_rate_key)

    generation_key: Mapped[int] = mapped_column(Integer)
    generation: Mapped["Generation"] = relationship(back_populates="pokemon_species",
                                            primaryjoin="Generation.id == PokemonSpecies.generation_key",
                                            foreign_keys=generation_key)

    egg_group_1: Mapped["EggGroup"] = relationship(back_populates="species_egg_group_1",
                                            primaryjoin="EggGroup.id == PokemonSpecies.egg_group_1_key",
                                            foreign_keys=egg_group_1_key)
    egg_group_2: Mapped["EggGroup"] = relationship(back_populates="species_egg_group_2",
                                            primaryjoin="EggGroup.id == PokemonSpecies.egg_group_2_key",
                                            foreign_keys=egg_group_2_key)
    
    color: Mapped["PokemonColor"] = relationship(back_populates="pokemon_species",
                                            primaryjoin="PokemonColor.id == PokemonSpecies.color_key",
                                            foreign_keys=color_key)
    
    shape: Mapped["PokemonShape"] = relationship(back_populates="pokemon_species",
                                            primaryjoin="PokemonShape.id == PokemonSpecies.shape_key",
                                            foreign_keys=shape_key)
    
    # Right now this is one-to-one
    # I may want to change this to many-to-one
    evolution_chain: Mapped["EvolutionChain"] = relationship(#back_populates="species",
                                            primaryjoin="EvolutionChain.id == PokemonSpecies.evolution_chain_key",
                                            foreign_keys=evolution_chain_key)
    
    party_evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="party_species",
                                                                            primaryjoin="PokemonSpecies.id == foreign(EvolutionDetail.party_species_key)")
    
    trade_evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="trade_species",
                                                                            primaryjoin="PokemonSpecies.id == foreign(EvolutionDetail.trade_species_key)")
    
    habitat: Mapped["PokemonHabitat"] = relationship(back_populates="pokemon_species",
                                                     primaryjoin="PokemonHabitat.id == PokemonSpecies.habitat_key",
                                                     foreign_keys=habitat_key)
    
    pal_park_encounters: Mapped[List["PalParkEncounter"]] = relationship(back_populates="pokemon_species",
                                                                         primaryjoin="PokemonSpecies.id == foreign(PalParkEncounter.pokemon_species_key)")
    
    names: Mapped[List["PokemonName"]] = relationship(back_populates="object_ref",
                                                      primaryjoin="PokemonSpecies.id == foreign(PokemonName.object_key)")
    flavor_text_entries: Mapped[List["PokemonSpeciesFlavorText"]] = relationship(back_populates="object_ref",
                                                      primaryjoin="PokemonSpecies.id == foreign(PokemonSpeciesFlavorText.object_key)")
    form_descriptions: Mapped[List["PokemonFormDescription"]] = relationship(back_populates="object_ref",
                                                      primaryjoin="PokemonSpecies.id == foreign(PokemonFormDescription.object_key)")
    genera: Mapped[List["PokemonGenus"]] = relationship(back_populates="object_ref",
                                                      primaryjoin="PokemonSpecies.id == foreign(PokemonGenus.object_key)")
    
    # map nat dex number to PokemonSpecies object
    _cache: Dict[int, "PokemonSpecies"] = {}
    _name_cache: Dict[str, "PokemonSpecies"] = {}

    @classmethod
    def get_species(cls, cache_key: int|str) -> Optional["PokemonSpecies"]:
        if type(cache_key) is int:
            return cls._get_species_by_nat_dex(cache_key)
        elif type(cache_key) is str:
            return cls._get_species_by_name(cache_key)
        else:
            # No cache implemented for type
            return None

    @classmethod
    def _get_species_by_nat_dex(cls, nat_dex: int) -> Optional["PokemonSpecies"]:
        if nat_dex not in cls._cache:
            with Session() as session:
                species: PokemonSpecies = session.scalars(select(PokemonSpecies).filter_by(national_dex_number=nat_dex)).first()
                if species:
                    cls._cache[species.national_dex_number] = species
                    cls._name_cache[species.name] = species
        return cls._cache.get(nat_dex)
    
    @classmethod
    def _get_species_by_name(cls, name: str) -> Optional["PokemonSpecies"]:
        if name not in cls._name_cache:
            with Session() as session:
                species: PokemonSpecies = session.scalars(select(PokemonSpecies).filter_by(name=name)).first()
                if species:
                    cls._cache[species.national_dex_number] = species
                    cls._name_cache[species.name] = species
        return cls._name_cache.get(name)

    @classmethod
    def parse_species(cls,data):
        atts = {}
        atts['national_dex_number'] = data.id
        atts['name'] = data.name
        atts['order'] = data.order
        atts['gender_rate'] = data.gender_rate
        atts['capture_rate'] = data.capture_rate
        atts['base_happiness'] = data.base_happiness
        atts['is_baby'] = data.is_baby
        atts['is_legendary'] = data.is_legendary
        atts['is_mythical'] = data.is_mythical
        atts['hatch_counter'] = data.hatch_counter
        atts['has_gender_differences'] = data.has_gender_differences
        atts['forms_switchable'] = data.forms_switchable


    def __init__(self):
        pass

# Stats
class PokemonStat(Base):
    # Used for both battle stats and pokeathlon stats
    __tablename__ = "PokemonStat"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    game_index: Mapped[Optional[int]] = mapped_column(Integer)
    is_battle_only: Mapped[Optional[bool]] = mapped_column(Boolean)
    damage_class_key: Mapped[Optional[int]] = mapped_column(Integer)

    """ affecting_moves: Mapped[List["MoveStatAffect"]] = relationship(back_populates="stat",
                                                                   primaryjoin="PokemonStat.id == foreign(MoveStatAffect.stat_key)") """
    changing_moves: Mapped[List["MoveStatChange"]] = relationship(back_populates="stat",
                                                                   primaryjoin="PokemonStat.id == foreign(MoveStatChange.stat_key)") 
    
    decreasing_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="decreased_stat",
                                                              primaryjoin="PokemonStat.id == foreign(PokemonNature.decreased_stat_key)")
    increasing_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="increased_stat",
                                                              primaryjoin="PokemonStat.id == foreign(PokemonNature.increased_stat_key)")
    decreasing_pokeathlon_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="decreased_pokeathlon_stat",
                                                              primaryjoin="PokemonStat.id == foreign(PokemonNature.decreased_pokeathlon_stat_key)")
    increasing_pokeathlon_natures: Mapped[List["PokemonNature"]] = relationship(back_populates="increased_pokeathlon_stat",
                                                              primaryjoin="PokemonStat.id == foreign(PokemonNature.increased_pokeathlon_stat_key)")
    characteristics: Mapped[List["PokemonCharacteristic"]] = relationship(back_populates="highest_stat",
                                                              primaryjoin="PokemonStat.id == foreign(PokemonCharacteristic.highest_stat_key)")

    damage_class: Mapped["DamageClass"] = relationship(primaryjoin="PokemonStat.damage_class_key == DamageClass.id",
                                                       foreign_keys=damage_class_key)

    names: Mapped[List["PokemonStatName"]] = relationship(back_populates="object_ref",
                                                          primaryjoin="PokemonStat.id == foreign(PokemonStatName.object_key)")

""" class MoveStatAffect(Base):
    __tablename__ = "MoveStatAffect"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    move_key: Mapped[int] = mapped_column(Integer)
    stat_key: Mapped[int] = mapped_column(Integer)
    change: Mapped[int] = mapped_column(TinyInteger)

    move: Mapped["PokemonMove"] = relationship(back_populates="affecting_stats",
                                               primaryjoin="MoveStatAffect.move_key == PokemonMove.id",
                                               foreign_keys=move_key)
    stat: Mapped["PokemonStat"] = relationship(back_populates="affecting_moves",
                                               primaryjoin="MoveStatAffect.stat_key == PokemonStat.id",
                                               foreign_keys=stat_key) """

# Types
class PokemonType(Base): 
    __tablename__ = "PokemonType"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    generation_introduced_key: Mapped[int] = mapped_column(Integer)
    damage_class_key: Mapped[int] = mapped_column(Integer)

    generation_introduced: Mapped["Generation"] = relationship(back_populates="types_introduced",
                                                               primaryjoin="PokemonType.generation_introduced_key == Generation.id",
                                                               foreign_keys=generation_introduced_key)
    #generations: Mapped[List["Generation"]] = relationship
    damage_class: Mapped["DamageClass"] = relationship(back_populates="types",
                                                       primaryjoin="PokemonType.damage_class_key == DamageClass.id",
                                                       foreign_keys=damage_class_key)

    offensive_relations: Mapped[List["PokemonTypeRelation"]] = relationship(back_populates="offensive_type",
                                                                            primaryjoin="PokemonType.id == foreign(PokemonTypeRelation.offensive_type_key)")
    defensive_relations: Mapped[List["PokemonTypeRelation"]] = relationship(back_populates="defensive_type",
                                                                            primaryjoin="PokemonType.id == foreign(PokemonTypeRelation.defensive_type_key)")

    main_types: Mapped[List["Pokemon"]] = relationship(back_populates="type_1",
                                                              primaryjoin="PokemonType.id == foreign(Pokemon.type_1_key)")
    secondary_types: Mapped[List["Pokemon"]] = relationship(back_populates="type_2",
                                                              primaryjoin="PokemonType.id == foreign(Pokemon.type_2_key)")
    moves: Mapped[List["Move"]] = relationship(back_populates="move_type",
                                               primaryjoin="PokemonType.id == foreign(Move.move_type_key)")
    names: Mapped[List["PokemonTypeName"]] = relationship(back_populates="object_ref",
                                                          primaryjoin="PokemonType.id == foreign(PokemonTypeName.id)")
    
    move_type_evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="known_move_type",
                                                                                primaryjoin="PokemonType.id == foreign(EvolutionDetail.known_move_type_key)")
    
    party_evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="party_type",
                                                                                primaryjoin="PokemonType.id == foreign(EvolutionDetail.party_type_key)")

    game_indices: Mapped[List["TypeGameIndex"]] = relationship(back_populates="object_ref",
                                                               primaryjoin="PokemonType.id == foreign(TypeGameIndex.object_key)")

class PastTypeLink(Base):
    __tablename__ = "PastTypeLink"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    last_generation_key: Mapped[int] = mapped_column(Integer)
    pokemon_key: Mapped[int] = mapped_column(Integer)
    past_type_key: Mapped[int] = mapped_column(Integer)

    last_generation: Mapped["Generation"] = relationship(primaryjoin="PastTypeLink.last_generation_key == Generation.id",
                                                         foreign_keys=last_generation_key)
    pokemon: Mapped["Pokemon"] = relationship(back_populates="past_types",
                                            primaryjoin="Pokemon.id == PastTypeLink.pokemon_key",
                                            foreign_keys=pokemon_key)
    
    #uni-drectional? No need to reference on PokemonTYpe?
    past_type: Mapped["PokemonType"] = relationship(primaryjoin="PastTypeLink.past_type_key == PokemonType.id",
                                                    foreign_keys=past_type_key)


class PokemonTypeRelation(Base):
    __tablename__ = "PokemonTypeRelation"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    offensive_type_key: Mapped[int] = mapped_column(Integer)
    defensive_type_key: Mapped[int] = mapped_column(Integer)
    generation_key: Mapped[Optional[int]] = mapped_column(Integer)
    damage_multiplier: Mapped[float] = mapped_column(Float)

    offensive_type: Mapped["PokemonType"] = relationship(back_populates="offensive_relations",
                                                         primaryjoin="PokemonTypeRelation.offensive_type_key == PokemonType.id",
                                                         foreign_keys=offensive_type_key)
    defensive_type: Mapped["PokemonType"] = relationship(back_populates="defensive_relations",
                                                         primaryjoin="PokemonTypeRelation.defensive_type_key == PokemonType.id",
                                                         foreign_keys=defensive_type_key)
    generation: Mapped["Generation"] = relationship(primaryjoin="PokemonTypeRelation.generation_key == Generation.id",
                                                    foreign_keys=generation_key)
