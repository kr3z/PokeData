from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Boolean

from Base import Base, TinyInteger

if TYPE_CHECKING:
    from Locations import Location
    from Items import Item
    from Moves import Move
    from Pokemon import Pokemon, PokemonSpecies, PokemonType
    from TextEntries import EvolutionTriggerName

class EvolutionChain(Base):
    __tablename__ = "EvolutionChain"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    is_baby: Mapped[bool] = mapped_column(Boolean)
    baby_trigger_item_key: Mapped[Optional[int]] = mapped_column(Integer)
    #chain_key: Mapped[int] = mapped_column(Integer)
    evolves_from_key: Mapped[Optional[int]] = mapped_column(Integer)
    species_key: Mapped[int] = mapped_column(Integer)

    baby_trigger_item: Mapped["Item"] = relationship(#back_populates="baby_trigger_for",
                                                     primaryjoin="EvolutionChain.baby_trigger_item_key == Item.id",
                                                     foreign_keys=baby_trigger_item_key)
    #chain: Mapped["ChainLink"] = relationship
    evolves_from: Mapped["EvolutionChain"] = relationship(back_populates="evolves_to", remote_side=id,
                                                          primaryjoin="EvolutionChain.evolves_from_key == EvolutionChain.id",
                                                          foreign_keys=evolves_from_key)
    evolves_to: Mapped[List["EvolutionChain"]] = relationship(back_populates="evolves_from",
                                                              primaryjoin="EvolutionChain.id == foreign(EvolutionChain.evolves_from_key)")
    evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="evolution_chain",
                                                                      primaryjoin="EvolutionChain.id == foreign(EvolutionDetail.evolution_chain_key)")
    species: Mapped["PokemonSpecies"] = relationship(#back_populates="evolution_chain",
                                                     primaryjoin="EvolutionChain.species_key == PokemonSpecies.id",
                                                     foreign_keys=species_key)
                                                     


""" class ChainLink(Base):
    __tablename__ = "ChainLink"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    is_baby: Mapped[bool] = mapped_column(Boolean)
    species_key: Mapped[int] = mapped_column(Integer)

    species
"""



class EvolutionDetail(Base):
    __tablename__ = "EvolutionDetail"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    evolution_chain_key: Mapped[int] = mapped_column(Integer)
    pokemon_key: Mapped[int] = mapped_column(Integer)
    trigger_key: Mapped[int] = mapped_column(Integer)
    item_key: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[int]] = mapped_column(Integer) # What is this?
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

    evolution_chain: Mapped["EvolutionChain"] = relationship(back_populates="evolution_details",
                                                             primaryjoin="EvolutionDetail.evolution_chain_key == EvolutionChain.id",
                                                             foreign_keys=evolution_chain_key)
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

class EvolutionTrigger(Base):
    __tablename__ = "EvolutionTrigger"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    names: Mapped[List["EvolutionTriggerName"]] = relationship(back_populates="object_ref",
                                                               primaryjoin="EvolutionTrigger.id == foreign(EvolutionTriggerName.object_key)")
    evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="trigger",
                                                                   primaryjoin="EvolutionTrigger.id == foreign(EvolutionDetail.trigger_key)")