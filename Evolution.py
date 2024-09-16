import pandas as pd
from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Boolean, UniqueConstraint

from Base import Base, TinyInteger, PokeApiResource, get_next_id, CSVData, CSVResource, ManyToOneAttrs

if TYPE_CHECKING:
    from Locations import Location
    from Items import Item
    from Moves import Move
    from Pokemon import Pokemon, PokemonSpecies, PokemonType, PokemonGender
    from TextEntries import EvolutionTriggerName

class EvolutionChain(Base, PokeApiResource):
    __tablename__ = "EvolutionChain"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    baby_trigger_item_key: Mapped[Optional[int]] = mapped_column(Integer)

    baby_trigger_item: Mapped["Item"] = relationship(back_populates="baby_trigger_for",
                                                     primaryjoin="EvolutionChain.baby_trigger_item_key == Item.id",
                                                     foreign_keys=baby_trigger_item_key, cascade="save-update")
    
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EvolutionChain_PokeApiId"),
    )
    csv_data: CSVData = CSVData(**{"primary_csv": "evolution_chains.csv",
                          "relationships": {"baby_trigger_item_id": ManyToOneAttrs("baby_trigger_item","baby_trigger_item_key")}})
    _cache: Dict[int, "EvolutionChain"] = {}

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["EvolutionChain"]:
        chains = []
        for id_, chain_data in df.iterrows():
            poke_api_id = id_
            chain = cls(poke_api_id=poke_api_id)
            cls._cache[chain.poke_api_id] = chain
            chains.append(chain)
        return chains
    
    def __init__(self, poke_api_id: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id

    def compare(self, data):
        pass


class EvolutionDetail(Base, PokeApiResource):
    __tablename__ = "EvolutionDetail"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    pokemon_key: Mapped[Optional[int]] = mapped_column(Integer)

    evolved_species_key: Mapped[int] = mapped_column(Integer)
    trigger_key: Mapped[int] = mapped_column(Integer)
    item_key: Mapped[Optional[int]] = mapped_column(Integer)
    gender_key: Mapped[Optional[int]] = mapped_column(Integer)
    location_key: Mapped[Optional[int]] = mapped_column(Integer)
    held_item_key: Mapped[Optional[int]] = mapped_column(Integer)
    known_move_key: Mapped[Optional[int]] = mapped_column(Integer)
    known_move_type_key: Mapped[Optional[int]] = mapped_column(Integer)
    party_species_key: Mapped[Optional[int]] = mapped_column(Integer)
    party_type_key: Mapped[Optional[int]] = mapped_column(Integer)
    trade_species_key: Mapped[Optional[int]] = mapped_column(Integer)

    min_level: Mapped[Optional[int]] = mapped_column(TinyInteger)
    min_happiness: Mapped[Optional[int]] = mapped_column(SmallInteger)
    min_beauty: Mapped[Optional[int]] = mapped_column(SmallInteger)
    min_affection: Mapped[Optional[int]] = mapped_column(SmallInteger)
    needs_overworld_rain: Mapped[bool] = mapped_column(Boolean)
    relative_physical_stats: Mapped[Optional[int]] = mapped_column(TinyInteger)
    time_of_day: Mapped[Optional[str]] = mapped_column(String(10))
    turn_upside_down: Mapped[bool] = mapped_column(Boolean)

    pokemon: Mapped["Pokemon"] = relationship(back_populates="evolution_details", cascade="save-update",
                                              primaryjoin="EvolutionDetail.pokemon_key == Pokemon.id",
                                              foreign_keys=pokemon_key)
    evolved_species: Mapped["PokemonSpecies"] = relationship(back_populates="evolution_details", cascade="save-update",
                                                             primaryjoin="EvolutionDetail.evolved_species_key == PokemonSpecies.id",
                                                             foreign_keys=evolved_species_key)
    trigger: Mapped["EvolutionTrigger"] = relationship(back_populates="evolution_details", cascade="save-update",
                                                       primaryjoin="EvolutionDetail.trigger_key == EvolutionTrigger.id",
                                                       foreign_keys=trigger_key)
    item: Mapped["Item"] = relationship(back_populates="evolution_details", cascade="save-update",
                                        primaryjoin="EvolutionDetail.item_key == Item.id",
                                        foreign_keys=item_key)
    gender: Mapped["PokemonGender"] = relationship(cascade="save-update", primaryjoin="EvolutionDetail.gender_key == PokemonGender.id",
                                            foreign_keys=gender_key)
    location: Mapped["Location"] = relationship(back_populates="evolution_details", cascade="save-update",
                                                primaryjoin="EvolutionDetail.location_key == Location.id",
                                                foreign_keys=location_key)
    held_item: Mapped["Item"] = relationship(back_populates="held_evolution_details", cascade="save-update",
                                        primaryjoin="EvolutionDetail.held_item_key == Item.id",
                                        foreign_keys=held_item_key)
    known_move: Mapped["Move"] = relationship(back_populates="known_move_evolution_details", cascade="save-update",
                                              primaryjoin="EvolutionDetail.known_move_key == Move.id",
                                              foreign_keys=known_move_key)
    known_move_type: Mapped["PokemonType"] = relationship(back_populates="move_type_evolution_details", cascade="save-update",
                                                          primaryjoin="EvolutionDetail.known_move_type_key == PokemonType.id",
                                                          foreign_keys=known_move_type_key)
    party_species: Mapped["PokemonSpecies"] = relationship(back_populates="party_evolution_details", cascade="save-update",
                                                           primaryjoin="EvolutionDetail.party_species_key == PokemonSpecies.id",
                                                           foreign_keys=party_species_key)
    party_type: Mapped["PokemonType"] = relationship(back_populates="party_evolution_details", cascade="save-update",
                                                           primaryjoin="EvolutionDetail.party_type_key == PokemonType.id",
                                                           foreign_keys=party_type_key)
    trade_species: Mapped["PokemonSpecies"] = relationship(back_populates="trade_evolution_details", cascade="save-update",
                                                           primaryjoin="EvolutionDetail.trade_species_key == PokemonSpecies.id",
                                                           foreign_keys=trade_species_key)

    _cache: Dict[int, "EvolutionDetail"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_evolution.csv",
                          "relationships": {"evolved_species_id": ManyToOneAttrs("evolved_species","evolved_species_key"),
                                            "evolution_trigger_id": ManyToOneAttrs("trigger","trigger_key"),
                                            "trigger_item_id": ManyToOneAttrs("item","item_key"),
                                            "gender_id": ManyToOneAttrs("gender","gender_key"),
                                            "location_id": ManyToOneAttrs("location","location_key"),
                                            "held_item_id": ManyToOneAttrs("held_item","held_item_key"),
                                            "known_move_id": ManyToOneAttrs("known_move", "known_move_key"),
                                            "known_move_type_id": ManyToOneAttrs("known_move_type","known_move_type_key"),
                                            "party_species_id": ManyToOneAttrs("party_species","party_species_key"),
                                            "party_type_id": ManyToOneAttrs("party_type","party_type_key"),
                                            "trade_species_id": ManyToOneAttrs("trade_species","trade_species_key")}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EvolutionDetail_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["EvolutionDetail"]:
        details = []
        for id_, detail_data in df.iterrows():
            poke_api_id = id_
            min_level = detail_data.minimum_level
            time_of_day = detail_data.time_of_day
            min_happiness = detail_data.minimum_happiness
            min_beauty = detail_data.minimum_beauty
            min_affection = detail_data.minimum_affection
            relative_physical_stats = detail_data.relative_physical_stats
            needs_overworld_rain = detail_data.needs_overworld_rain
            turn_upside_down = detail_data.turn_upside_down
            detail = cls(poke_api_id=poke_api_id, min_level=min_level, min_happiness=min_happiness, min_beauty=min_beauty, min_affection=min_affection,
                      needs_overworld_rain=needs_overworld_rain, relative_physical_stats=relative_physical_stats, time_of_day=time_of_day,
                      turn_upside_down=turn_upside_down)
        
            cls._cache[detail.poke_api_id] = detail
            details.append(detail)
        return details


    def __init__(self, poke_api_id: int, min_level: int = None, min_happiness: int = None, min_beauty: int = None, min_affection: int = None,
                 needs_overworld_rain: bool = False, relative_physical_stats: int = None, time_of_day: str = None, turn_upside_down: bool = False):
        self.id = get_next_id()

        self.poke_api_id = poke_api_id
        self.min_level = min_level
        self.min_happiness = min_happiness
        self.min_beauty = min_beauty
        self.min_affection = min_affection
        self.needs_overworld_rain = needs_overworld_rain
        self.relative_physical_stats = relative_physical_stats
        self.time_of_day = time_of_day
        self.turn_upside_down = turn_upside_down

    def compare(self, details_data):
        if self.min_level != details_data.minimum_level:
            self.min_level = details_data.minimum_level
        if self.min_happiness != details_data.minimum_happiness:
            self.min_happiness = details_data.minimum_happiness
        if self.min_beauty != details_data.minimum_beauty:
            self.min_beauty = details_data.minimum_beauty
        if self.min_affection != details_data.minimum_affection:
            self.min_affection = details_data.minimum_affection
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

    names: Mapped[List["EvolutionTriggerName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                               primaryjoin="EvolutionTrigger.id == foreign(EvolutionTriggerName.object_key)")
    evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="trigger", cascade="save-update",
                                                                   primaryjoin="EvolutionTrigger.id == foreign(EvolutionDetail.trigger_key)")
    
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_EvolutionTrigger_PokeApiId"),
    )
    csv_data: CSVData = CSVData(**{"primary_csv": "evolution_triggers.csv",
                          "relationships": {}})
    _cache: Dict[int, "EvolutionTrigger"] = {}

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["EvolutionTrigger"]:
        triggers = []
        for id_, trigger_data in df.iterrows():
            poke_api_id = id_
            name = trigger_data.identifier
            trigger = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[trigger.poke_api_id] = trigger
            triggers.append(trigger)
        return triggers
    
    def __init__(self, poke_api_id: int, name: str):
        self.poke_api_id = poke_api_id
        self.id = get_next_id()
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier