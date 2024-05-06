from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Boolean, UniqueConstraint

from Base import Base, TinyInteger, PokeApiResource, get_next_id

if TYPE_CHECKING:
    from Locations import Location
    from Items import Item
    from Moves import Move
    from Pokemon import Pokemon, PokemonSpecies, PokemonType
    from TextEntries import EvolutionTriggerName

class EvolutionChain(Base, PokeApiResource):
    __tablename__ = "EvolutionChain"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    baby_trigger_item_key: Mapped[Optional[int]] = mapped_column(Integer)
    chain_key: Mapped[int] = mapped_column(Integer)

    baby_trigger_item: Mapped["Item"] = relationship(#back_populates="baby_trigger_for",
                                                     primaryjoin="EvolutionChain.baby_trigger_item_key == Item.id",
                                                     foreign_keys=baby_trigger_item_key)
    
    chain: Mapped["ChainLink"] = relationship(back_populates="evolution_chain",
                                              primaryjoin="EvolutionChain.chain_key == ChainLink.id",
                                              foreign_keys=chain_key)
    
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EvolutionChain_PokeApiId"),
    )

    _cache: Dict[int, "EvolutionChain"] = {}

    @classmethod
    def parse_data(cls,data) -> "EvolutionChain":
        poke_api_id = data.id
        evolution_chain = cls(poke_api_id=poke_api_id)
        cls._cache[evolution_chain.poke_api_id] = evolution_chain
        return evolution_chain
    
    def __init__(self, poke_api_id: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id

    def compare(self, data):
        pass

class ChainLink(Base):
    __tablename__ = "ChainLink"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    is_baby: Mapped[bool] = mapped_column(Boolean)
    species_key: Mapped[int] = mapped_column(Integer)
    evolves_from_key: Mapped[Optional[int]] = mapped_column(Integer)
    #chain: Mapped["ChainLink"] = relationship
    evolves_from: Mapped["ChainLink"] = relationship(back_populates="evolves_to", remote_side=id,
                                                          primaryjoin="ChainLink.evolves_from_key == ChainLink.id",
                                                          foreign_keys=evolves_from_key)
    evolves_to: Mapped[List["ChainLink"]] = relationship(back_populates="evolves_from",
                                                              primaryjoin="ChainLink.id == foreign(ChainLink.evolves_from_key)")
    evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="chain_link",
                                                                      primaryjoin="ChainLink.id == foreign(EvolutionDetail.evolution_chain_key)")
    species: Mapped["PokemonSpecies"] = relationship(#back_populates="evolution_chain",
                                                     primaryjoin="ChainLink.species_key == PokemonSpecies.id",
                                                     foreign_keys=species_key)

    __table_args__ = (
        UniqueConstraint("species_key",name="ux_ChainLink_SpeciesKey"),
    )

    @classmethod
    def parse_data(cls,data) -> "ChainLink":
        #poke_api_id = data.id
        chain = cls(is_baby = data.is_baby)
        #cls._cache[evolution_chain.poke_api_id] = evolution_chain
        return chain
    
    def __init__(self, is_baby: bool):
        self.id = get_next_id()
        self.is_baby = is_baby

    def compare(self, data):
        if self.is_baby != data.is_baby:
            self.is_baby = data.is_baby


class EvolutionDetail(Base):
    __tablename__ = "EvolutionDetail"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    chain_link_key: Mapped[int] = mapped_column(Integer)
    pokemon_key: Mapped[int] = mapped_column(Integer)
    trigger_key: Mapped[int] = mapped_column(Integer)
    item_key: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[int]] = mapped_column(TinyInteger) # What is this?
    held_item_key: Mapped[Optional[int]] = mapped_column(Integer)
    known_move_key: Mapped[Optional[int]] = mapped_column(Integer)
    known_move_type_key: Mapped[Optional[int]] = mapped_column(Integer)
    location_key: Mapped[Optional[int]] = mapped_column(Integer)
    min_level: Mapped[Optional[int]] = mapped_column(TinyInteger)
    min_happiness: Mapped[Optional[int]] = mapped_column(SmallInteger)
    min_beauty: Mapped[Optional[int]] = mapped_column(SmallInteger)
    min_affection: Mapped[Optional[int]] = mapped_column(SmallInteger)
    needs_overworld_rain: Mapped[bool] = mapped_column(Boolean)
    party_species_key: Mapped[Optional[int]] = mapped_column(Integer)
    party_type_key: Mapped[Optional[int]] = mapped_column(Integer)
    relative_physical_stats: Mapped[Optional[int]] = mapped_column(TinyInteger)
    time_of_day: Mapped[Optional[str]] = mapped_column(String(10))
    trade_species_key: Mapped[Optional[int]] = mapped_column(Integer)
    turn_upside_down: Mapped[bool] = mapped_column(Boolean)

    chain_link: Mapped["ChainLink"] = relationship(back_populates="evolution_details",
                                                             primaryjoin="EvolutionDetail.evolution_chain_key == ChainLink.id",
                                                             foreign_keys=chain_link_key)
    pokemon: Mapped["Pokemon"] = relationship(back_populates="evolution_details",
                                              primaryjoin="EvolutionDetail.pokemon_key == Pokemon.id",
                                              foreign_keys=pokemon_key)
    trigger: Mapped["EvolutionTrigger"] = relationship(back_populates="evolution_details",
                                                       primaryjoin="EvolutionDetail.trigger_key == EvolutionTrigger.id",
                                                       foreign_keys=trigger_key)
    item: Mapped["Item"] = relationship(back_populates="evolution_details",
                                        primaryjoin="EvolutionDetail.item_key == Item.id",
                                        foreign_keys=item_key)
    held_item: Mapped["Item"] = relationship(back_populates="held_evolution_details",
                                        primaryjoin="EvolutionDetail.held_item_key == Item.id",
                                        foreign_keys=held_item_key)
    known_move: Mapped["Move"] = relationship(back_populates="known_move_evolution_details",
                                              primaryjoin="EvolutionDetail.known_move_key == Move.id",
                                              foreign_keys=known_move_key)
    known_move_type: Mapped["PokemonType"] = relationship(back_populates="move_type_evolution_details",
                                                          primaryjoin="EvolutionDetail.known_move_type_key == PokemonType.id",
                                                          foreign_keys=known_move_type_key)
    location: Mapped["Location"] = relationship(back_populates="evolution_details",
                                                primaryjoin="EvolutionDetail.location_key == Location.id",
                                                foreign_keys=location_key)
    party_species: Mapped["PokemonSpecies"] = relationship(back_populates="party_evolution_details",
                                                           primaryjoin="EvolutionDetail.party_species_key == PokemonSpecies.id",
                                                           foreign_keys=party_species_key)
    party_type: Mapped["PokemonType"] = relationship(back_populates="party_evolution_details",
                                                           primaryjoin="EvolutionDetail.party_type_key == PokemonType.id",
                                                           foreign_keys=party_type_key)
    trade_species: Mapped["PokemonSpecies"] = relationship(back_populates="trade_evolution_details",
                                                           primaryjoin="EvolutionDetail.trade_species_key == PokemonSpecies.id",
                                                           foreign_keys=trade_species_key)
    
    @classmethod
    def parse_data(cls, details_data) -> "EvolutionDetail":
        gender = details_data.gender
        min_level = details_data.min_level
        min_happiness = details_data.min_happiness
        min_beauty = details_data.min_beauty
        min_affection = details_data.min_affection
        needs_overworld_rain = details_data.needs_overworld_rain
        relative_physical_stats = details_data.relative_physical_stats
        time_of_day = details_data.time_of_day
        turn_upside_down = details_data.turn_upside_down
        details = cls(gender=gender, min_level=min_level, min_happiness=min_happiness, min_beauty=min_beauty, min_affection=min_affection,
                      needs_overworld_rain=needs_overworld_rain, relative_physical_stats=relative_physical_stats, time_of_day=time_of_day,
                      turn_upside_down=turn_upside_down, details=details)
        
        # cache?
        return details


    def __init__(self, gender: int = None, min_level: int = None, min_happiness: int = None, min_beauty: int = None, min_affection: int = None,
                 needs_overworld_rain: bool = False, relative_physical_stats: int = None, time_of_day: str = None, turn_upside_down: bool = False):
        self.id = get_next_id()

        self.gender = gender
        self.min_level = min_level
        self.min_happiness = min_happiness
        self.min_beauty = min_beauty
        self.min_affection = min_affection
        self.needs_overworld_rain = needs_overworld_rain
        self.relative_physical_stats = relative_physical_stats
        self.time_of_day = time_of_day
        self.turn_upside_down = turn_upside_down

    def compare(self, details_data):
        if self.gender != details_data.gender:
            self.gender = details_data.gender
        if self.min_level != details_data.min_level:
            self.min_level = details_data.min_level
        if self.min_happiness != details_data.min_happiness:
            self.min_happiness = details_data.min_happiness
        if self.min_beauty != details_data.min_beauty:
            self.min_beauty = details_data.min_beauty
        if self.min_affection != details_data.min_affection:
            self.min_affection = details_data.min_affection
        if self.needs_overworld_rain != details_data.needs_overworld_rain:
            self.needs_overworld_rain = details_data.needs_overworld_rain
        if self.relative_physical_stats != details_data.relative_physical_stats:
            self.relative_physical_stats = details_data.relative_physical_stats
        if self.time_of_day != details_data.time_of_day:
            self.time_of_day = details_data.time_of_day
        if self.turn_upside_down != details_data.turn_upside_down:
            self.turn_upside_down = details_data.turn_upside_down

class EvolutionTrigger(Base, PokeApiResource):
    __tablename__ = "EvolutionTrigger"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    names: Mapped[List["EvolutionTriggerName"]] = relationship(back_populates="object_ref",
                                                               primaryjoin="EvolutionTrigger.id == foreign(EvolutionTriggerName.object_key)")
    evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="trigger",
                                                                   primaryjoin="EvolutionTrigger.id == foreign(EvolutionDetail.trigger_key)")
    
    @classmethod
    def parse_data(cls, data) -> "EvolutionTrigger":
        poke_api_id = data.id
        trigger = cls(poke_api_id = poke_api_id, name = data.name)
        cls._cache[trigger.poke_api_id] = trigger

        return trigger
    
    def __init__(self, poke_api_id: int, name: str):
        self.poke_api_id = poke_api_id
        self.id = get_next_id()
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name