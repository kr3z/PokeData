from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Float, Computed, UniqueConstraint, Index, Boolean
from sqlalchemy import Table, Column, ForeignKey

from Base import Base, TinyInteger, MoveLearnMethodToVersionGroupLink

if TYPE_CHECKING:
    from Contests import ContestType, ContestEffect, SuperContestEffect, ContestChain, SuperContestChain
    from Evolution import EvolutionDetail
    from Games import Generation, VersionGroup
    from Pokemon import Pokemon, PokemonType, PokemonStat, PokemonMove, MoveBattleStylePreference
    from Items import Item
    from TextEntries import MoveEffectChange, MoveEffect, MoveFlavorText, MoveName
    from TextEntries import DamageClassDescription, DamageClassName, PastMoveEffect
    from TextEntries import MoveAilmentName, MoveBattleStyleName, MoveCategoryDescription
    from TextEntries import MoveLearnMethodName, MoveLearnMethodDescription, MoveTargetDescription, MoveTargetName

class Move(Base):
    __tablename__ = "Move"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    accuracy: Mapped[int] = mapped_column(TinyInteger)
    effect_chance: Mapped[int] = mapped_column(TinyInteger)
    pp: Mapped[int] = mapped_column(TinyInteger)
    priority: Mapped[int] = mapped_column(TinyInteger)
    power: Mapped[int] = mapped_column(SmallInteger)

    #MoveMetaData
    min_hits: Mapped[Optional[int]] = mapped_column(TinyInteger)
    max_hits: Mapped[Optional[int]] = mapped_column(TinyInteger)
    min_turns: Mapped[Optional[int]] = mapped_column(TinyInteger)
    max_turns: Mapped[Optional[int]] = mapped_column(TinyInteger)
    drain: Mapped[int] = mapped_column(TinyInteger)
    healing: Mapped[int] = mapped_column(TinyInteger)
    crit_rate: Mapped[int] = mapped_column(TinyInteger)
    ailment_chance: Mapped[int] = mapped_column(TinyInteger)
    flinch_chance: Mapped[int] = mapped_column(TinyInteger)
    stat_chance: Mapped[int] = mapped_column(TinyInteger)

    contest_type_key: Mapped[Optional[int]] = mapped_column(Integer)
    contest_effect_key: Mapped[Optional[int]] = mapped_column(Integer)
    super_contest_effect_key: Mapped[Optional[int]] = mapped_column(Integer)

    damage_class_key: Mapped[int] = mapped_column(Integer)
    move_type_key: Mapped[int] = mapped_column(Integer)
    generation_key: Mapped[int] = mapped_column(Integer)
    ailment_key: Mapped[int] = mapped_column(Integer)
    category_key: Mapped[int] = mapped_column(Integer)
    target_key: Mapped[int] = mapped_column(Integer)

    contest_combos: Mapped[List["ContestChain"]] = relationship(back_populates="move",
                                                                primaryjoin="Move.id == foreign(ContestChain.move_key)")
    super_contest_combos: Mapped[List["SuperContestChain"]] = relationship(back_populates="move",
                                                                primaryjoin="Move.id == foreign(SuperContestChain.move_key)")
    contest_type: Mapped["ContestType"] = relationship(back_populates="moves",
                                                       primaryjoin="Move.contest_type_key == ContestType.id",
                                                       foreign_keys=contest_type_key)
    contest_effect: Mapped["ContestEffect"] = relationship(back_populates="moves",
                                                           primaryjoin="Move.contest_effect_key == ContestEffect.id",
                                                           foreign_keys=contest_effect_key)
    super_contest_effect: Mapped["SuperContestEffect"] = relationship(back_populates="moves",
                                                           primaryjoin="Move.super_contest_effect_key == SuperContestEffect.id",
                                                           foreign_keys=super_contest_effect_key)

    damage_class: Mapped["DamageClass"] = relationship(back_populates="moves",
                                                       primaryjoin="Move.damage_class_key == DamageClass.id",
                                                       foreign_keys=damage_class_key)

    learned_by_pokemon: Mapped[List["PokemonMove"]] = relationship(back_populates="move",
                                            primaryjoin="Move.id == foreign(PokemonMove.move_key)")
    
    generation: Mapped["Generation"] = relationship(back_populates="moves",
                                                    primaryjoin="Move.generation_key == Generation.id",
                                                    foreign_keys=generation_key)
    ailment: Mapped["MoveAilment"] = relationship(back_populates="moves",
                                                  primaryjoin="Move.ailment_key == MoveAilment.id",
                                                  foreign_keys=ailment_key)
    category: Mapped["MoveCategory"] = relationship(back_populates="moves",
                                                  primaryjoin="Move.category_key == MoveCategory.id",
                                                  foreign_keys=category_key)

    machines: Mapped[List["Machine"]] = relationship(back_populates="move",
                                                     primaryjoin="Move.id == foreign(Machine.move_key)")
    past_values: Mapped[List["PastMoveStatValues"]] = relationship(back_populates="move",
                                                                   primaryjoin="Move.id == foreign(PastMoveStatValues.move_key)")
    stat_changes: Mapped[List["MoveStatChange"]] = relationship(back_populates="move",
                                                                primaryjoin="Move.id == foreign(MoveStatChange.move_key)")
    target: Mapped["MoveTarget"] = relationship(back_populates="moves",
                                                primaryjoin="Move.target_key == MoveTarget.id",
                                                foreign_keys=target_key)
    move_type: Mapped["PokemonType"] = relationship(back_populates="moves",
                                                    primaryjoin="Move.move_type_key == PokemonType.id",
                                                    foreign_keys=move_type_key)
    
    known_move_evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="known_move",
                                                                                 primaryjoin="Move.id == foreign(EvolutionDetail.known_move_key)")

    effect_entries: Mapped[List["MoveEffect"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="Move.id == foreign(MoveEffect.object_key)")
    effect_changes: Mapped[List["MoveEffectChange"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="Move.id == foreign(MoveEffectChange.object_key)")
    flavor_text_entries: Mapped[List["MoveFlavorText"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="Move.id == foreign(MoveFlavorText.object_key)")
    names: Mapped[List["MoveName"]] = relationship(back_populates="object_ref",
                                                              primaryjoin="Move.id == foreign(MoveName.object_key)")

class MoveStatChange(Base):
    __tablename__ = "MoveStatChange"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    change: Mapped[int] = mapped_column(TinyInteger)
    stat_key: Mapped[int] = mapped_column(Integer)
    move_key: Mapped[int] = mapped_column(Integer)
    
    stat: Mapped["PokemonStat"] = relationship(back_populates="changing_moves",
                                               primaryjoin="MoveStatChange.stat_key == PokemonStat.id",
                                               foreign_keys=stat_key)
    move: Mapped["Move"] = relationship(back_populates="stat_changes",
                                        primaryjoin="MoveStatChange.move_key == Move.id",
                                        foreign_keys=move_key)

class PastMoveStatValues(Base):
    __tablename__ = "PastMoveStatValue"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    move_key: Mapped[int] = mapped_column(Integer)
    accuracy: Mapped[int] = mapped_column(TinyInteger)
    effect_chance: Mapped[int] = mapped_column(TinyInteger)
    power: Mapped[int] = mapped_column(SmallInteger)
    pp: Mapped[int] = mapped_column(TinyInteger)
    
    move_type_key: Mapped[int] = mapped_column(Integer)
    version_group_key: Mapped[int] = mapped_column(Integer)

    move: Mapped["Move"] = relationship(back_populates="past_values",
                                        primaryjoin="PastMoveStatValues.move_key == Move.id",
                                        foreign_keys=move_key)
    move_type: Mapped["PokemonType"] = relationship(primaryjoin="PastMoveStatValues.move_type_key == PokemonType.id",
                                                    foreign_keys=move_type_key)
    version_group: Mapped["VersionGroup"] = relationship(primaryjoin="PastMoveStatValues.version_group_key == VersionGroup.id",
                                                         foreign_keys=version_group_key)
    effect_entries: Mapped[List["PastMoveEffect"]] = relationship(back_populates="object_ref",
                                                                  primaryjoin="PastMoveStatValues.id == foreign(PastMoveEffect.object_key)")

class MoveAilment(Base):
    __tablename__ = "MoveAilment"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    moves: Mapped[List["Move"]] = relationship(back_populates="ailment",
                                               primaryjoin="MoveAilment.id == foreign(Move.ailment_key)")
    names: Mapped[List["MoveAilmentName"]] = relationship(back_populates="object_ref",
                                                                  primaryjoin="MoveAilment.id == foreign(MoveAilmentName.object_key)")

class MoveBattleStyle(Base):
    __tablename__ = "MoveBattleStyle"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    preference: Mapped[List["MoveBattleStylePreference"]] = relationship(back_populates="move_battle_style",
                                            primaryjoin="MoveBattleStyle.id == foreign(MoveBattleStylePreference.move_battle_style_key)")

    names: Mapped[List["MoveBattleStyleName"]] = relationship(back_populates="object_ref",
                                                                  primaryjoin="MoveBattleStyle.id == foreign(MoveBattleStyleName.object_key)")

class MoveCategory(Base):
    __tablename__ = "MoveCategory"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    moves: Mapped[List["Move"]] = relationship(back_populates="category",
                                               primaryjoin="MoveCategory.id == foreign(Move.category_key)")
    descriptions: Mapped[List["MoveCategoryDescription"]] = relationship(back_populates="object_ref",
                                                                  primaryjoin="MoveCategory.id == foreign(MoveCategoryDescription.object_key)")

class DamageClass(Base): 
    __tablename__ = "DamageClass"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    types: Mapped[List["PokemonType"]] = relationship(back_populates="damage_class",
                                                      primaryjoin="DamageClass.id == foreign(PokemonType.damage_class_key)")
    moves: Mapped[List["Move"]] = relationship(back_populates="damage_class",
                                               primaryjoin="DamageClass.id == foreign(Move.damage_class_key)")
    descriptions: Mapped[List["DamageClassDescription"]] = relationship(back_populates="object_ref",
                                                                  primaryjoin="DamageClass.id == foreign(DamageClassDescription.object_key)")
    names: Mapped[List["DamageClassName"]] = relationship(back_populates="object_ref",
                                                                  primaryjoin="DamageClass.id == foreign(DamageClassName.object_key)")

class MoveLearnMethod(Base): 
    __tablename__ = "MoveLearnMethod"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    descriptions: Mapped[List["MoveLearnMethodDescription"]] = relationship(back_populates="object_ref",
                                                                  primaryjoin="MoveLearnMethod.id == foreign(MoveLearnMethodDescription.object_key)")
    names: Mapped[List["MoveLearnMethodName"]] = relationship(back_populates="object_ref",
                                                                  primaryjoin="MoveLearnMethod.id == foreign(MoveLearnMethodName.object_key)")
    
    version_groups: Mapped[List["VersionGroup"]] = relationship(back_populates="move_learn_methods", secondary=MoveLearnMethodToVersionGroupLink)

    pokemon_moves: Mapped[List["PokemonMove"]] = relationship(back_populates="move_learn_method",
                                            primaryjoin="MoveLearnMethod.id == foreign(PokemonMove.move_learn_method_key)")

class MoveTarget(Base):
    __tablename__ = "MoveTarget"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    moves: Mapped[List["Move"]] = relationship(back_populates="target",
                                               primaryjoin="MoveTarget.id == foreign(Move.target_key)")
    
    descriptions: Mapped[List["MoveTargetDescription"]] = relationship(back_populates="object_ref",
                                                                  primaryjoin="MoveTarget.id == foreign(MoveTargetDescription.object_key)")
    names: Mapped[List["MoveTargetName"]] = relationship(back_populates="object_ref",
                                                                  primaryjoin="MoveTarget.id == foreign(MoveTargetName.object_key)")

class Machine(Base):
    __tablename__ = "Machine"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    item_key: Mapped[int] = mapped_column(Integer)
    move_key: Mapped[int] = mapped_column(Integer)
    version_group_key: Mapped[int] = mapped_column(Integer)

    item: Mapped["Item"] = relationship(back_populates="machines",
                                        primaryjoin="Machine.item_key == Item.id",
                                        foreign_keys=item_key)
    move: Mapped["Move"] = relationship(back_populates="machines",
                                        primaryjoin="Machine.move_key == Move.id",
                                        foreign_keys=move_key)
    version_group: Mapped["VersionGroup"] = relationship(back_populates="machines",
                                                         primaryjoin="Machine.version_group_key == VersionGroup.id",
                                                         foreign_keys=version_group_key)