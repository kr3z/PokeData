from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Float, Computed, UniqueConstraint, Index, Boolean
from sqlalchemy import Table, Column, ForeignKey

from Base import Base, TinyInteger, MoveLearnMethodToVersionGroupLink, get_next_id, PokeApiResource, ContestComboLink, SuperContestComboLink

if TYPE_CHECKING:
    from Contests import ContestType, ContestEffect, SuperContestEffect#, ContestChain, SuperContestChain
    from Evolution import EvolutionDetail
    from Games import Generation, VersionGroup
    from Pokemon import Pokemon, PokemonType, PokemonStat, PokemonMove, MoveBattleStylePreference
    from Items import Item
    from TextEntries import MoveEffectChange, MoveEffect, MoveFlavorText, MoveName
    from TextEntries import DamageClassDescription, DamageClassName, PastMoveEffect
    from TextEntries import MoveAilmentName, MoveBattleStyleName, MoveCategoryDescription
    from TextEntries import MoveLearnMethodName, MoveLearnMethodDescription, MoveTargetDescription, MoveTargetName

class Move(Base, PokeApiResource):
    __tablename__ = "Move"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    accuracy: Mapped[Optional[int]] = mapped_column(TinyInteger)
    effect_chance: Mapped[Optional[int]] = mapped_column(TinyInteger)
    pp: Mapped[Optional[int]] = mapped_column(TinyInteger)
    priority: Mapped[Optional[int]] = mapped_column(TinyInteger)
    power: Mapped[Optional[int]] = mapped_column(SmallInteger)

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

    """ contest_combos: Mapped[List["ContestChain"]] = relationship(back_populates="move",cascade="save-update",
                                                                primaryjoin="Move.id == foreign(ContestChain.move_key)")
    super_contest_combos: Mapped[List["SuperContestChain"]] = relationship(back_populates="move",cascade="save-update",
                                                                primaryjoin="Move.id == foreign(SuperContestChain.move_key)") """
    
    lead_in_contest_combo_moves: Mapped[List["Move"]] = relationship(back_populates="follow_up_contest_combo_moves", secondary=ContestComboLink,  cascade="save-update",
                                                                     primaryjoin="Move.id == ContestComboLink.c.follow_up_move_key",
                                                                     secondaryjoin="Move.id == ContestComboLink.c.lead_move_key")

    follow_up_contest_combo_moves: Mapped[List["Move"]] = relationship(back_populates="lead_in_contest_combo_moves", secondary=ContestComboLink,  cascade="save-update",
                                                                     primaryjoin="Move.id == ContestComboLink.c.lead_move_key",
                                                                     secondaryjoin="Move.id == ContestComboLink.c.follow_up_move_key")
    
    lead_in_super_contest_combo_moves: Mapped[List["Move"]] = relationship(back_populates="follow_up_super_contest_combo_moves", secondary=SuperContestComboLink,  cascade="save-update",
                                                                     primaryjoin="Move.id == SuperContestComboLink.c.follow_up_move_key",
                                                                     secondaryjoin="Move.id == SuperContestComboLink.c.lead_move_key")

    follow_up_super_contest_combo_moves: Mapped[List["Move"]] = relationship(back_populates="lead_in_super_contest_combo_moves", secondary=SuperContestComboLink,  cascade="save-update",
                                                                     primaryjoin="Move.id == SuperContestComboLink.c.lead_move_key",
                                                                     secondaryjoin="Move.id == SuperContestComboLink.c.follow_up_move_key")

    contest_type: Mapped["ContestType"] = relationship(back_populates="moves", cascade="save-update",
                                                       primaryjoin="Move.contest_type_key == ContestType.id",
                                                       foreign_keys=contest_type_key)
    contest_effect: Mapped["ContestEffect"] = relationship(#back_populates="moves", 
                                                           cascade="save-update",
                                                           primaryjoin="Move.contest_effect_key == ContestEffect.id",
                                                           foreign_keys=contest_effect_key)
    super_contest_effect: Mapped["SuperContestEffect"] = relationship(back_populates="moves", cascade="save-update",
                                                           primaryjoin="Move.super_contest_effect_key == SuperContestEffect.id",
                                                           foreign_keys=super_contest_effect_key)

    damage_class: Mapped["DamageClass"] = relationship(back_populates="moves", cascade="save-update",
                                                       primaryjoin="Move.damage_class_key == DamageClass.id",
                                                       foreign_keys=damage_class_key)

    learned_by_pokemon: Mapped[List["PokemonMove"]] = relationship(back_populates="move",cascade="save-update",
                                            primaryjoin="Move.id == foreign(PokemonMove.move_key)")
    
    generation: Mapped["Generation"] = relationship(back_populates="moves", cascade="save-update",
                                                    primaryjoin="Move.generation_key == Generation.id",
                                                    foreign_keys=generation_key)
    ailment: Mapped["MoveAilment"] = relationship(back_populates="moves", cascade="save-update",
                                                  primaryjoin="Move.ailment_key == MoveAilment.id",
                                                  foreign_keys=ailment_key)
    category: Mapped["MoveCategory"] = relationship(back_populates="moves", cascade="save-update",
                                                  primaryjoin="Move.category_key == MoveCategory.id",
                                                  foreign_keys=category_key)

    machines: Mapped[List["Machine"]] = relationship(back_populates="move", cascade="save-update",
                                                     primaryjoin="Move.id == foreign(Machine.move_key)")
    past_values: Mapped[List["PastMoveStatValues"]] = relationship(back_populates="move",cascade="save-update",
                                                                   primaryjoin="Move.id == foreign(PastMoveStatValues.move_key)")
    stat_changes: Mapped[List["MoveStatChange"]] = relationship(back_populates="move",cascade="save-update",
                                                                primaryjoin="Move.id == foreign(MoveStatChange.move_key)")
    target: Mapped["MoveTarget"] = relationship(back_populates="moves",cascade="save-update",
                                                primaryjoin="Move.target_key == MoveTarget.id",
                                                foreign_keys=target_key)
    move_type: Mapped["PokemonType"] = relationship(back_populates="moves", cascade="save-update",
                                                    primaryjoin="Move.move_type_key == PokemonType.id",
                                                    foreign_keys=move_type_key)
    
    known_move_evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="known_move",cascade="save-update",
                                                                                 primaryjoin="Move.id == foreign(EvolutionDetail.known_move_key)")

    effect_entries: Mapped[List["MoveEffect"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="Move.id == foreign(MoveEffect.object_key)")
    effect_changes: Mapped[List["MoveEffectChange"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="Move.id == foreign(MoveEffectChange.object_key)")
    flavor_text_entries: Mapped[List["MoveFlavorText"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="Move.id == foreign(MoveFlavorText.object_key)")
    names: Mapped[List["MoveName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="Move.id == foreign(MoveName.object_key)")
    
    _cache: Dict[int, "Move"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Move_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "Move":
        poke_api_id = data.id_
        name = data.name
        accuracy = data.accuracy
        effect_chance = data.effect_chance
        pp = data.pp
        priority = data.priority
        power = data.power
        
        #meta
        min_hits = data.meta.min_hits
        max_hits = data.meta.max_hits
        min_turns = data.meta.min_turns
        max_turns = data.meta.max_turns
        drain = data.meta.drain
        healing = data.meta.healing
        crit_rate = data.meta.crit_rate
        ailment_chance = data.meta.ailment_chance
        flinch_chance = data.meta.flinch_chance
        stat_chance = data.meta.stat_chance

        move = cls(poke_api_id=poke_api_id, name=name, accuracy=accuracy, effect_chance=effect_chance, pp=pp, priority=priority, power=power, min_hits=min_hits, max_hits=max_hits,
                   min_turns=min_turns, max_turns=max_turns, drain=drain, healing=healing, crit_rate=crit_rate, ailment_chance=ailment_chance, flinch_chance=flinch_chance, stat_chance=stat_chance)
        cls._cache[move.poke_api_id] = move
        return move
    
    def __init__(self, poke_api_id: int, name: str, accuracy: int, effect_chance: int, pp: int, priority: int, power: int, min_hits: int, max_hits: int,
                   min_turns: int, max_turns: int, drain: int, healing: int, crit_rate: int, ailment_chance: int, flinch_chance: int, stat_chance: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.accuracy = accuracy
        self.effect_chance = effect_chance
        self.pp = pp
        self.priority = priority
        self.power = power
        
        #meta
        self.min_hits = min_hits
        self.max_hits = max_hits
        self.min_turns = min_turns
        self.max_turns = max_turns
        self.drain = drain
        self.healing = healing
        self.crit_rate = crit_rate
        self.ailment_chance = ailment_chance
        self.flinch_chance = flinch_chance
        self.stat_chance = stat_chance

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name
        if self.accuracy != data.accuracy:
            self.accuracy = data.accuracy
        if self.effect_chance != data.effect_chance:
            self.effect_chance = data.effect_chance
        if self.pp != data.pp:
            self.pp = data.pp
        if self.priority != data.priority:
            self.priority = data.priority
        if self.power != data.power:
            self.power = data.power
        
        #meta
        if self.min_hits != data.meta.min_hits:
            self.min_hits = data.meta.min_hits
        if self.max_hits != data.meta.max_hits:
            self.max_hits = data.meta.max_hits
        if self.min_turns != data.meta.min_turns:
            self.min_turns = data.meta.min_turns
        if self.max_turns != data.meta.max_turns:
            self.max_turns = data.meta.max_turns
        if self.drain != data.meta.drain:
            self.drain = data.meta.drain
        if self.healing != data.meta.healing:
            self.healing = data.meta.healing
        if self.crit_rate != data.meta.crit_rate:
            self.crit_rate = data.meta.crit_rate
        if self.ailment_chance != data.meta.ailment_chance:
            self.ailment_chance = data.meta.ailment_chance
        if self.flinch_chance != data.meta.flinch_chance:
            self.flinch_chance = data.meta.flinch_chance
        if self.stat_chance != data.meta.stat_chance:
            self.stat_chance = data.meta.stat_chance

class MoveStatChange(Base):
    __tablename__ = "MoveStatChange"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    change: Mapped[int] = mapped_column(TinyInteger)
    stat_key: Mapped[int] = mapped_column(Integer)
    move_key: Mapped[int] = mapped_column(Integer)
    
    stat: Mapped["PokemonStat"] = relationship(back_populates="changing_moves", cascade="save-update",
                                               primaryjoin="MoveStatChange.stat_key == PokemonStat.id",
                                               foreign_keys=stat_key)
    move: Mapped["Move"] = relationship(back_populates="stat_changes", cascade="save-update",
                                        primaryjoin="MoveStatChange.move_key == Move.id",
                                        foreign_keys=move_key)
    
    __table_args__ = (
        UniqueConstraint("move_key","stat_key",name="ux_MoveStatChange_Move_Stat"),
    )

    @classmethod
    def parse_data(cls,data) -> "MoveStatChange":
        #poke_api_id = data.id_
        change = data.change

        stat_change = cls(change=change)
        #cls._cache[ailment.poke_api_id] = ailment
        return stat_change
    
    def __init__(self, change: int):
        self.id = get_next_id()
        self.change = change

    def compare(self, data):
        if self.change != data.change:
            self.change = data.change

class PastMoveStatValues(Base):
    __tablename__ = "PastMoveStatValue"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    move_key: Mapped[int] = mapped_column(Integer)
    accuracy: Mapped[Optional[int]] = mapped_column(TinyInteger)
    effect_chance: Mapped[Optional[int]] = mapped_column(TinyInteger)
    power: Mapped[Optional[int]] = mapped_column(SmallInteger)
    pp: Mapped[Optional[int]] = mapped_column(TinyInteger)
    
    move_type_key: Mapped[Optional[int]] = mapped_column(Integer)
    version_group_key: Mapped[int] = mapped_column(Integer)

    move: Mapped["Move"] = relationship(back_populates="past_values", cascade="save-update",
                                        primaryjoin="PastMoveStatValues.move_key == Move.id",
                                        foreign_keys=move_key)
    move_type: Mapped["PokemonType"] = relationship(primaryjoin="PastMoveStatValues.move_type_key == PokemonType.id",
                                                    foreign_keys=move_type_key)
    version_group: Mapped["VersionGroup"] = relationship(primaryjoin="PastMoveStatValues.version_group_key == VersionGroup.id",
                                                         foreign_keys=version_group_key)
    effect_entries: Mapped[List["PastMoveEffect"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="PastMoveStatValues.id == foreign(PastMoveEffect.object_key)")
    
    __table_args__ = (
        UniqueConstraint("move_key","version_group_key",name="ux_PastMoveStatValues_Move_VG"),
    )

    @classmethod
    def parse_data(cls,data) -> "PastMoveStatValues":
        #poke_api_id = data.id_
        accuracy = data.accuracy
        effect_chance = data.effect_chance
        power = data.power
        pp = data.pp

        past_value = cls(accuracy=accuracy, effect_chance=effect_chance, power=power, pp=pp)
        #cls._cache[ailment.poke_api_id] = ailment
        return past_value
    
    def __init__(self, accuracy: int, effect_chance: int, power: int, pp: int):
        self.id = get_next_id()
        self.accuracy = accuracy
        self.effect_chance = effect_chance
        self.power = power
        self.pp = pp

    def compare(self, data):
        if self.accuracy != data.accuracy:
            self.accuracy = data.accuracy
        if self.effect_chance != data.effect_chance:
            self.effect_chance = data.effect_chance
        if self.power != data.power:
            self.power = data.power
        if self.pp != data.pp:
            self.pp = data.pp

class MoveAilment(Base, PokeApiResource):
    __tablename__ = "MoveAilment"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    moves: Mapped[List["Move"]] = relationship(back_populates="ailment", cascade="save-update",
                                               primaryjoin="MoveAilment.id == foreign(Move.ailment_key)")
    names: Mapped[List["MoveAilmentName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveAilment.id == foreign(MoveAilmentName.object_key)")
    
    _cache: Dict[int, "MoveAilment"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveAilment_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "MoveAilment":
        poke_api_id = data.id_
        name = data.name

        ailment = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[ailment.poke_api_id] = ailment
        return ailment
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name

class MoveBattleStyle(Base, PokeApiResource):
    __tablename__ = "MoveBattleStyle"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    preference: Mapped[List["MoveBattleStylePreference"]] = relationship(back_populates="move_battle_style", cascade="save-update",
                                            primaryjoin="MoveBattleStyle.id == foreign(MoveBattleStylePreference.move_battle_style_key)")

    names: Mapped[List["MoveBattleStyleName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveBattleStyle.id == foreign(MoveBattleStyleName.object_key)")
    
    _cache: Dict[int, "MoveBattleStyle"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveBattleStyle_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "MoveBattleStyle":
        poke_api_id = data.id_
        name = data.name

        mbs = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[mbs.poke_api_id] = mbs
        return mbs
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name

class MoveCategory(Base, PokeApiResource):
    __tablename__ = "MoveCategory"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    moves: Mapped[List["Move"]] = relationship(back_populates="category", cascade="save-update",
                                               primaryjoin="MoveCategory.id == foreign(Move.category_key)")
    descriptions: Mapped[List["MoveCategoryDescription"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveCategory.id == foreign(MoveCategoryDescription.object_key)")
    
    _cache: Dict[int, "MoveCategory"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveCategory_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "MoveCategory":
        poke_api_id = data.id_
        name = data.name

        cat = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[cat.poke_api_id] = cat
        return cat
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name


class DamageClass(Base, PokeApiResource):
    __tablename__ = "DamageClass"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    types: Mapped[List["PokemonType"]] = relationship(back_populates="damage_class", cascade="save-update",
                                                      primaryjoin="DamageClass.id == foreign(PokemonType.damage_class_key)")
    moves: Mapped[List["Move"]] = relationship(back_populates="damage_class", cascade="save-update",
                                               primaryjoin="DamageClass.id == foreign(Move.damage_class_key)")
    descriptions: Mapped[List["DamageClassDescription"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="DamageClass.id == foreign(DamageClassDescription.object_key)")
    names: Mapped[List["DamageClassName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="DamageClass.id == foreign(DamageClassName.object_key)")
    
    _cache: Dict[int, "DamageClass"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_DamageClass_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "DamageClass":
        poke_api_id = data.id_
        name = data.name

        dc = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[dc.poke_api_id] = dc
        return dc
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name

class MoveLearnMethod(Base, PokeApiResource): 
    __tablename__ = "MoveLearnMethod"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    descriptions: Mapped[List["MoveLearnMethodDescription"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveLearnMethod.id == foreign(MoveLearnMethodDescription.object_key)")
    names: Mapped[List["MoveLearnMethodName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveLearnMethod.id == foreign(MoveLearnMethodName.object_key)")
    
    version_groups: Mapped[List["VersionGroup"]] = relationship(back_populates="move_learn_methods", secondary=MoveLearnMethodToVersionGroupLink,  cascade="save-update")

    pokemon_moves: Mapped[List["PokemonMove"]] = relationship(back_populates="move_learn_method", cascade="save-update",
                                            primaryjoin="MoveLearnMethod.id == foreign(PokemonMove.move_learn_method_key)")
    
    _cache: Dict[int, "MoveLearnMethod"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveLearnMethod_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "MoveLearnMethod":
        poke_api_id = data.id_
        name = data.name

        method = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[method.poke_api_id] = method
        return method
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name

class MoveTarget(Base, PokeApiResource):
    __tablename__ = "MoveTarget"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    moves: Mapped[List["Move"]] = relationship(back_populates="target", cascade="save-update",
                                               primaryjoin="MoveTarget.id == foreign(Move.target_key)")
    
    descriptions: Mapped[List["MoveTargetDescription"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveTarget.id == foreign(MoveTargetDescription.object_key)")
    names: Mapped[List["MoveTargetName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveTarget.id == foreign(MoveTargetName.object_key)")
    
    _cache: Dict[int, "MoveTarget"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveTarget_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "MoveTarget":
        poke_api_id = data.id_
        name = data.name

        target = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[target.poke_api_id] = target
        return target
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name

class Machine(Base, PokeApiResource):
    __tablename__ = "Machine"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    item_key: Mapped[int] = mapped_column(Integer)
    move_key: Mapped[int] = mapped_column(Integer)
    version_group_key: Mapped[int] = mapped_column(Integer)

    item: Mapped["Item"] = relationship(back_populates="machines", cascade="save-update",
                                        primaryjoin="Machine.item_key == Item.id",
                                        foreign_keys=item_key)
    move: Mapped["Move"] = relationship(back_populates="machines", cascade="save-update",
                                        primaryjoin="Machine.move_key == Move.id",
                                        foreign_keys=move_key)
    version_group: Mapped["VersionGroup"] = relationship(back_populates="machines", cascade="save-update",
                                                         primaryjoin="Machine.version_group_key == VersionGroup.id",
                                                         foreign_keys=version_group_key)
    
    _cache: Dict[int, "Machine"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Machine_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "Machine":
        poke_api_id = data.id_

        machine = cls(poke_api_id=poke_api_id)
        cls._cache[machine.poke_api_id] = machine
        return machine
    
    def __init__(self, poke_api_id: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id

    def compare(self, data):
        pass