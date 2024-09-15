import pandas as pd
from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Float, Computed, UniqueConstraint, Index, Boolean
from sqlalchemy import Table, Column, ForeignKey

from Base import Base, TinyInteger, MoveLearnMethodToVersionGroupLink, get_next_id, PokeApiResource, ContestComboLink, SuperContestComboLink, ManyToOneAttrs, CSVData, CSVResource, MergeCSV, GroupByCSV, ManyToManyAttr, MoveToMoveFlagLink

if TYPE_CHECKING:
    from Contests import ContestType, ContestEffect, SuperContestEffect#, ContestChain, SuperContestChain
    from Evolution import EvolutionDetail
    from Games import Generation, VersionGroup
    from Pokemon import Pokemon, PokemonType, PokemonStat, PokemonMove, MoveBattleStylePreference
    from Items import Item
    from TextEntries import MoveEffectChange, MoveEffect, MoveFlavorText, MoveName
    from TextEntries import DamageClassDescription, DamageClassName, MoveEffectEffect, MoveEffectChangeText
    from TextEntries import MoveAilmentName, MoveBattleStyleName, MoveCategoryDescription
    from TextEntries import MoveLearnMethodName, MoveLearnMethodDescription, MoveTargetDescription, MoveTargetName
    from TextEntries import MoveFlagName, MoveFlagDescription

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
    drain: Mapped[Optional[int]] = mapped_column(TinyInteger)
    healing: Mapped[Optional[int]] = mapped_column(TinyInteger)
    crit_rate: Mapped[Optional[int]] = mapped_column(TinyInteger)
    ailment_chance: Mapped[Optional[int]] = mapped_column(TinyInteger)
    flinch_chance: Mapped[Optional[int]] = mapped_column(TinyInteger)
    stat_chance: Mapped[Optional[int]] = mapped_column(TinyInteger)

    contest_type_key: Mapped[Optional[int]] = mapped_column(Integer)
    contest_effect_key: Mapped[Optional[int]] = mapped_column(Integer)
    super_contest_effect_key: Mapped[Optional[int]] = mapped_column(Integer)

    damage_class_key: Mapped[int] = mapped_column(Integer)
    move_type_key: Mapped[int] = mapped_column(Integer)
    generation_key: Mapped[int] = mapped_column(Integer)
    ailment_key: Mapped[Optional[int]] = mapped_column(Integer)
    category_key: Mapped[Optional[int]] = mapped_column(Integer)
    target_key: Mapped[int] = mapped_column(Integer)
    effect_key: Mapped[Optional[int]] = mapped_column(Integer)

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

    """ effect_entries: Mapped[List["MoveEffect"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="Move.id == foreign(MoveEffect.object_key)") """
    move_effect: Mapped["MoveEffect"] = relationship(back_populates="moves", cascade="save-update",
                                                     primaryjoin="Move.effect_key == MoveEffect.id",
                                                     foreign_keys=effect_key)
    
    move_flags: Mapped[List["MoveFlag"]] = relationship(back_populates="moves", secondary=MoveToMoveFlagLink,  cascade="save-update")
    """ effect_changes: Mapped[List["MoveEffectChange"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="Move.id == foreign(MoveEffectChange.object_key)") """
    """ effect_changes: Mapped[List["MoveEffectChange"]] = relationship(back_populates="move", cascade="save-update",
                                                              primaryjoin="Move.id == foreign(MoveEffectChange.move_ley)") """
    flavor_text_entries: Mapped[List["MoveFlavorText"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="Move.id == foreign(MoveFlavorText.object_key)")
    names: Mapped[List["MoveName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="Move.id == foreign(MoveName.object_key)")
    
    _cache: Dict[int, "Move"] = {}
    #_csv = "moves.csv"
    csv_data: CSVData = CSVData(**{"primary_csv": "moves.csv", 
                         "merge_csvs": (MergeCSV("move_meta.csv", "move_id"),
                                        MergeCSV("move_flag_map.csv", "move_id"),
                                        MergeCSV("contest_combos.csv", "first_move_id"),
                                        MergeCSV("super_contest_combos.csv", "first_move_id", rename_columns={'second_move_id':'super_second_move_id'}),),
                        "group_by": GroupByCSV(['move_flag_id','second_move_id','super_second_move_id'], 
                                               ['id','identifier','generation_id','type_id','power','pp','accuracy','priority','target_id','damage_class_id','effect_id','effect_chance','contest_type_id','contest_effect_id','super_contest_effect_id','meta_category_id','meta_ailment_id','min_hits','max_hits','min_turns','max_turns','drain','healing','crit_rate','ailment_chance','flinch_chance','stat_chance']),
                         "relationships": {
                             "generation_id": ManyToOneAttrs("generation","generation_key"),
                             "type_id": ManyToOneAttrs("move_type","move_type_key"),
                             "target_id": ManyToOneAttrs("target","target_key"),
                             "damage_class_id": ManyToOneAttrs("damage_class","damage_class_key"),
                             "effect_id": ManyToOneAttrs("move_effect", "effect_key"),
                             "contest_type_id": ManyToOneAttrs("contest_type","contest_type_key"),
                             "contest_effect_id": ManyToOneAttrs("contest_effect","contest_effect_key"),
                             "super_contest_effect_id": ManyToOneAttrs("super_contest_effect","super_contest_effect_key"),
                             "meta_category_id": ManyToOneAttrs("category","category_key"),
                             "meta_ailment_id": ManyToOneAttrs("ailment", "ailment_key"),
                             "move_flag_id": ManyToManyAttr("move_flags"),
                             "second_move_id": ManyToManyAttr("follow_up_contest_combo_moves"),
                             "super_second_move_id": ManyToManyAttr("follow_up_super_contest_combo_moves")}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Move_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["Move"]:
        moves = []
        for id_, move_data in df.iterrows():
            poke_api_id = id_
            name = move_data.identifier
            accuracy = move_data.accuracy
            effect_chance = move_data.effect_chance
            pp = move_data.pp
            priority = move_data.priority
            power = move_data.power

            min_hits = move_data.min_hits
            max_hits = move_data.max_hits
            min_turns = move_data.min_turns
            max_turns = move_data.max_turns
            drain = move_data.drain
            healing = move_data.healing
            crit_rate = move_data.crit_rate
            ailment_chance = move_data.ailment_chance
            flinch_chance = move_data.flinch_chance
            stat_chance = move_data.stat_chance

            move = cls(poke_api_id=poke_api_id, name=name, accuracy=accuracy, effect_chance=effect_chance, pp=pp, priority=priority, power=power, min_hits=min_hits, max_hits=max_hits,
                   min_turns=min_turns, max_turns=max_turns, drain=drain, healing=healing, crit_rate=crit_rate, ailment_chance=ailment_chance, flinch_chance=flinch_chance, stat_chance=stat_chance)
            cls._cache[move.poke_api_id] = move
            moves.append(move)
        return moves
    
    @classmethod
    def parse_data(cls,data) -> "Move":
        poke_api_id = data.id_
        name = data.identifier
        accuracy = data.accuracy
        effect_chance = data.effect_chance
        pp = data.pp
        priority = data.priority
        power = data.power
        
        #meta
        """ min_hits = data.meta.min_hits
        max_hits = data.meta.max_hits
        min_turns = data.meta.min_turns
        max_turns = data.meta.max_turns
        drain = data.meta.drain
        healing = data.meta.healing
        crit_rate = data.meta.crit_rate
        ailment_chance = data.meta.ailment_chance
        flinch_chance = data.meta.flinch_chance
        stat_chance = data.meta.stat_chance """

        min_hits = data.min_hits
        max_hits = data.max_hits
        min_turns = data.min_turns
        max_turns = data.max_turns
        drain = data.drain
        healing = data.healing
        crit_rate = data.crit_rate
        ailment_chance = data.ailment_chance
        flinch_chance = data.flinch_chance
        stat_chance = data.stat_chance

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
        if self.name != data.identifier:
            self.name = data.identifier
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
        """ if self.min_hits != data.meta.min_hits:
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
            self.stat_chance = data.meta.stat_chance """

        if self.min_hits != data.min_hits:
            self.min_hits = data.min_hits
        if self.max_hits != data.max_hits:
            self.max_hits = data.max_hits
        if self.min_turns != data.min_turns:
            self.min_turns = data.min_turns
        if self.max_turns != data.max_turns:
            self.max_turns = data.max_turns
        if self.drain != data.drain:
            self.drain = data.drain
        if self.healing != data.healing:
            self.healing = data.healing
        if self.crit_rate != data.crit_rate:
            self.crit_rate = data.crit_rate
        if self.ailment_chance != data.ailment_chance:
            self.ailment_chance = data.ailment_chance
        if self.flinch_chance != data.flinch_chance:
            self.flinch_chance = data.flinch_chance
        if self.stat_chance != data.stat_chance:
            self.stat_chance = data.stat_chance

### This isn't actually an API resource
### But it still has a poke_api_id so we can treat it as such
### This actually only has a poke_api_id and exists to provide a mapping
### between moves and effect text entries
class MoveEffect(Base, PokeApiResource):
    __tablename__ = "MoveEffect"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)

    moves: Mapped[List["Move"]] = relationship(back_populates="move_effect", cascade="save-update",
                                               primaryjoin="MoveEffect.id == foreign(Move.effect_key)")
    past_effects: Mapped[List["MoveEffectChange"]] = relationship(back_populates="effect", cascade="save-update",
                                                                  primaryjoin="MoveEffect.id == foreign(MoveEffectChange.effect_key)")
    
    effect_entries: Mapped[List["MoveEffectEffect"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="MoveEffect.id == foreign(MoveEffectEffect.object_key)") 

    _cache: Dict[int, "MoveEffect"] = {}
    #_csv = "move_effects.csv"
    #relationship_attr_map = {}  
    csv_data: CSVData = CSVData(**{"primary_csv": "move_effects.csv", "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveEffect_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["MoveEffect"]:
        effects = []
        for id_, effect_data in df.iterrows():
            poke_api_id = id_
            #name = effect_data.identifier
            effect = cls(poke_api_id=poke_api_id)
            cls._cache[effect.poke_api_id] = effect
            effects.append(effect)
        return effects
    
    """ @classmethod
    def parse_data(cls,data) -> "MoveEffect":
        poke_api_id = data.id_
        effect = cls(poke_api_id=poke_api_id)
        cls._cache[effect.poke_api_id] = effect
        return effect """
    
    def __init__(self, poke_api_id: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id

    def compare(self, data) -> bool:
        return False
    
class MoveEffectChange(Base, PokeApiResource):
    __tablename__ = "MoveEffectChange"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    effect_key: Mapped[int] = mapped_column(Integer)
    #move_key: Mapped[int] = mapped_column(Integer)
    changed_in_version_group_key: Mapped[int] = mapped_column(Integer)

    effect: Mapped["MoveEffect"] = relationship(back_populates="past_effects", cascade="save-update",
                                                primaryjoin="MoveEffectChange.effect_key == MoveEffect.id",
                                                foreign_keys=effect_key)
    """ move: Mapped["Move"] = relationship(back_populates="effect_changes", cascade="save-update",
                                                primaryjoin="MoveEffectChange.move_key == Move.id",
                                                foreign_keys=move_key) """
    changed_in_version_group: Mapped["VersionGroup"] = relationship(cascade="save-update",
                                                                    primaryjoin="MoveEffectChange.changed_in_version_group_key == VersionGroup.id",
                                                                    foreign_keys=changed_in_version_group_key)
    
    effect_entries: Mapped[List["MoveEffectChangeText"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="MoveEffectChange.id == foreign(MoveEffectChangeText.object_key)") 
    
    _cache: Dict[int, "MoveEffectChange"] = {}
    """ _csv = "move_effect_changelog.csv"
    relationship_attr_map = {"changed_in_version_group_id": ManyToOneAttrs("changed_in_version_group","changed_in_version_group_key"),
                             "effect_id": ManyToOneAttrs("effect", "effect_key")} """
                             #"move_id": ManyToOneAttrs("move", "move_key")} 
    csv_data: CSVData = CSVData(**{"primary_csv": "move_effect_changelog.csv",
                          "relationships": {"changed_in_version_group_id": ManyToOneAttrs("changed_in_version_group","changed_in_version_group_key"),
                                            "effect_id": ManyToOneAttrs("effect", "effect_key")}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveEffectChange_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["MoveEffectChange"]:
        changes = []
        for id_, change_data in df.iterrows():
            poke_api_id = id_
            #name = change_data.identifier
            change = cls(poke_api_id=poke_api_id)
            cls._cache[change.poke_api_id] = change
            changes.append(change)
        return changes
    
    @classmethod
    def parse_data(cls,data) -> "MoveEffectChange":
        poke_api_id = data.id_
        effect = cls(poke_api_id=poke_api_id)
        cls._cache[effect.poke_api_id] = effect
        return effect
    
    def __init__(self, poke_api_id: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id

    def compare(self, data) -> bool:
        return False

class MoveStatChange(Base, CSVResource):
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
    """ _csv = "move_meta_stat_changes.csv"
    relationship_attr_map = {"move_id": ManyToOneAttrs("move","move_key"),
                             "stat_id": ManyToOneAttrs("stat","stat_key")}   """
    csv_data: CSVData = CSVData(**{"primary_csv": "move_meta_stat_changes.csv", 
                         "relationships": {
                             "move_id": ManyToOneAttrs("move","move_key"),
                             "stat_id": ManyToOneAttrs("stat","stat_key")}})
    __table_args__ = (
        UniqueConstraint("move_key","stat_key",name="ux_MoveStatChange_Move_Stat"),
    )

    """ @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["MoveStatChange"]:
        stat_changes = []
        for id_, stat_change_data in df.iterrows():
            change = stat_change_data.change
            stat_change = cls(change=change)
            #cls._cache[value.poke_api_id] = value
            stat_changes.append(stat_change)
        return stat_changes """
    
    """ @classmethod
    def parse_data(cls,data) -> "MoveStatChange":
        #poke_api_id = data.id_
        change = data.change

        stat_change = cls(change=change)
        #cls._cache[ailment.poke_api_id] = ailment
        return stat_change """
    
    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.change = data.change

    def compare(self, data):
        #updated = False
        if self.change != data.change:
            self.change = data.change
            #updated = True
        #return updated

    def get_unique_key(self):
        return str(self.move.poke_api_id) + ":" + str(self.stat.poke_api_id)

class PastMoveStatValues(Base, CSVResource):
    __tablename__ = "PastMoveStatValue"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    move_key: Mapped[int] = mapped_column(Integer)
    accuracy: Mapped[Optional[int]] = mapped_column(TinyInteger)
    effect_chance: Mapped[Optional[int]] = mapped_column(TinyInteger)
    power: Mapped[Optional[int]] = mapped_column(SmallInteger)
    pp: Mapped[Optional[int]] = mapped_column(TinyInteger)
    priority: Mapped[Optional[int]] = mapped_column(TinyInteger)
    
    move_type_key: Mapped[Optional[int]] = mapped_column(Integer)
    version_group_key: Mapped[int] = mapped_column(Integer)

    move: Mapped["Move"] = relationship(back_populates="past_values", cascade="save-update",
                                        primaryjoin="PastMoveStatValues.move_key == Move.id",
                                        foreign_keys=move_key)
    move_type: Mapped["PokemonType"] = relationship(primaryjoin="PastMoveStatValues.move_type_key == PokemonType.id",cascade="save-update",
                                                    foreign_keys=move_type_key)
    version_group: Mapped["VersionGroup"] = relationship(primaryjoin="PastMoveStatValues.version_group_key == VersionGroup.id", cascade="save-update",
                                                         foreign_keys=version_group_key)
    """ effect_entries: Mapped[List["PastMoveEffect"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="PastMoveStatValues.id == foreign(PastMoveEffect.object_key)") """
    
    """ _csv = "move_changelog.csv"
    relationship_attr_map = {"changed_in_version_group_id": ManyToOneAttrs("version_group","version_group_key"),
                             "move_id": ManyToOneAttrs("move", "move_key")}  """
    csv_data: CSVData = CSVData(**{"primary_csv": "move_changelog.csv", 
                         "relationships": {
                             "changed_in_version_group_id": ManyToOneAttrs("version_group","version_group_key"),
                             "move_id": ManyToOneAttrs("move", "move_key")
                         }})
    __table_args__ = (
        UniqueConstraint("move_key","version_group_key",name="ux_PastMoveStatValues_Move_VG"),
    )

    """ @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["PastMoveStatValues"]:
        values = []
        for id_, value_data in df.iterrows():
            accuracy = value_data.accuracy
            effect_chance = value_data.effect_chance
            power = value_data.power
            pp = value_data.pp
            value = cls(accuracy=accuracy, effect_chance=effect_chance, power=power, pp=pp)
            #cls._cache[value.poke_api_id] = value
            values.append(value)
        return values """
    
    """ @classmethod
    def parse_data(cls,data) -> "PastMoveStatValues":
        #poke_api_id = data.id_
        accuracy = data.accuracy
        effect_chance = data.effect_chance
        power = data.power
        pp = data.pp

        past_value = cls(accuracy=accuracy, effect_chance=effect_chance, power=power, pp=pp)
        #cls._cache[ailment.poke_api_id] = ailment
        return past_value """
    
    #def __init__(self, accuracy: int, effect_chance: int, power: int, pp: int):
    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        self.accuracy = data.accuracy
        self.effect_chance = data.effect_chance
        self.power = data.power
        self.pp = data.pp
        self.priority = data.priority

    def compare(self, data: pd.Series):
        #updated = False
        if self.accuracy != data.accuracy:
            self.accuracy = data.accuracy
            #updated = True
        if self.effect_chance != data.effect_chance:
            self.effect_chance = data.effect_chance
            #updated = True
        if self.power != data.power:
            self.power = data.power
            #updated = True
        if self.pp != data.pp:
            self.pp = data.pp
            #updated = True
        if self.priority != data.priority:
            self.priority = data.priority
            #updated = True
        #return updated

    def get_unique_key(self):
        return str(self.version_group.poke_api_id) + ":" + str(self.move.poke_api_id)

class MoveAilment(Base, PokeApiResource):
    __tablename__ = "MoveAilment"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    moves: Mapped[List["Move"]] = relationship(back_populates="ailment", cascade="save-update",
                                               primaryjoin="MoveAilment.id == foreign(Move.ailment_key)")
    names: Mapped[List["MoveAilmentName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveAilment.id == foreign(MoveAilmentName.object_key)")
    
    _cache: Dict[int, "MoveAilment"] = {}
    #_csv = "move_meta_ailments.csv"
    #relationship_attr_map = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "move_meta_ailments.csv", "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveAilment_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["MoveAilment"]:
        ailments = []
        for id_, ailment_data in df.iterrows():
            poke_api_id = id_
            name = ailment_data.identifier
            ailment = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[ailment.poke_api_id] = ailment
            ailments.append(ailment)
        return ailments
    
    @classmethod
    def parse_data(cls,data) -> "MoveAilment":
        poke_api_id = data.id_
        name = data.identifier

        ailment = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[ailment.poke_api_id] = ailment
        return ailment
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

class MoveBattleStyle(Base, PokeApiResource):
    __tablename__ = "MoveBattleStyle"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    preference: Mapped[List["MoveBattleStylePreference"]] = relationship(back_populates="move_battle_style", cascade="save-update",
                                            primaryjoin="MoveBattleStyle.id == foreign(MoveBattleStylePreference.move_battle_style_key)")

    names: Mapped[List["MoveBattleStyleName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveBattleStyle.id == foreign(MoveBattleStyleName.object_key)")
    
    _cache: Dict[int, "MoveBattleStyle"] = {}
    #_csv = "move_battle_styles.csv"
    #relationship_attr_map = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "move_battle_styles.csv", "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveBattleStyle_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["MoveBattleStyle"]:
        styles = []
        for id_, style_data in df.iterrows():
            poke_api_id = id_
            name = style_data.identifier
            style = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[style.poke_api_id] = style
            styles.append(style)
        return styles
    
    @classmethod
    def parse_data(cls,data) -> "MoveBattleStyle":
        poke_api_id = data.id_
        name = data.identifier

        mbs = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[mbs.poke_api_id] = mbs
        return mbs
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

class MoveCategory(Base, PokeApiResource):
    __tablename__ = "MoveCategory"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    moves: Mapped[List["Move"]] = relationship(back_populates="category", cascade="save-update",
                                               primaryjoin="MoveCategory.id == foreign(Move.category_key)")
    descriptions: Mapped[List["MoveCategoryDescription"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveCategory.id == foreign(MoveCategoryDescription.object_key)")
    
    _cache: Dict[int, "MoveCategory"] = {}
    #_csv = "move_meta_categories.csv"
    #relationship_attr_map = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "move_meta_categories.csv", "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveCategory_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["MoveCategory"]:
        categories = []
        for id_, category_data in df.iterrows():
            poke_api_id = id_
            name = category_data.identifier
            category = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[category.poke_api_id] = category
            categories.append(category)
        return categories
    
    @classmethod
    def parse_data(cls,data) -> "MoveCategory":
        poke_api_id = data.id_
        name = data.identifier

        cat = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[cat.poke_api_id] = cat
        return cat
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier


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
    #_csv = "move_damage_classes.csv"
    #relationship_attr_map = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "move_damage_classes.csv", "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_DamageClass_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["DamageClass"]:
        dcs = []
        for id_, dc_data in df.iterrows():
            poke_api_id = id_
            name = dc_data.identifier
            dc = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[dc.poke_api_id] = dc
            dcs.append(dc)
        return dcs
    
    @classmethod
    def parse_data(cls,data) -> "DamageClass":
        poke_api_id = data.id_
        name = data.identifier

        dc = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[dc.poke_api_id] = dc
        return dc
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

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
    #_csv = "pokemon_move_methods.csv"
    #relationship_attr_map = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_move_methods.csv", 
                                   "merge_csvs": (MergeCSV("version_group_pokemon_move_methods.csv", "pokemon_move_method_id"),),
                                   "group_by": GroupByCSV(['version_group_id'], ['id','identifier']),
                                   "relationships": {"version_group_id": ManyToManyAttr("version_groups")}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveLearnMethod_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["MoveLearnMethod"]:
        methods = []
        for id_, method_data in df.iterrows():
            poke_api_id = id_
            name = method_data.identifier
            method = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[method.poke_api_id] = method
            methods.append(method)
        return methods
    
    @classmethod
    def parse_data(cls,data) -> "MoveLearnMethod":
        poke_api_id = data.id_
        name = data.identifier

        method = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[method.poke_api_id] = method
        return method
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

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
    #_csv = "move_targets.csv"
    #relationship_attr_map = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "move_targets.csv", "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveTarget_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["MoveTarget"]:
        targets = []
        for id_, target_data in df.iterrows():
            poke_api_id = id_
            name = target_data.identifier
            target = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[target.poke_api_id] = target
            targets.append(target)
        return targets
    
    @classmethod
    def parse_data(cls,data) -> "MoveTarget":
        poke_api_id = data.id_
        name = data.identifier

        target = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[target.poke_api_id] = target
        return target
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

class MoveFlag(Base, PokeApiResource): 
    __tablename__ = "MoveFlag"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    moves: Mapped[List["Move"]] = relationship(back_populates="move_flags", secondary=MoveToMoveFlagLink,  cascade="save-update")

    names: Mapped[List["MoveFlagName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveFlag.id == foreign(MoveFlagName.object_key)")
    
    descriptions: Mapped[List["MoveFlagDescription"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                                  primaryjoin="MoveFlag.id == foreign(MoveFlagDescription.object_key)")
    
    _cache: Dict[int, "MoveFlag"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "move_flags.csv", "relationships": {}})
    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_MoveFlag_PokeApiId"),
    )

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["MoveFlag"]:
        flags = []
        for id_, flag_data in df.iterrows():
            poke_api_id = id_
            name = flag_data.identifier
            flag = cls(poke_api_id=poke_api_id, name=name)
            cls._cache[flag.poke_api_id] = flag
            flags.append(flag)
        return flags
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.identifier:
            self.name = data.identifier

class Machine(Base, CSVResource):
    __tablename__ = "Machine"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    machine_number: Mapped[int] = mapped_column(SmallInteger)
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
    
    #_cache: Dict[int, "Machine"] = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "machines.csv", 
                                   "relationships": {"version_group_id": ManyToOneAttrs("version_group","version_group_key"),
                                                     "item_id": ManyToOneAttrs("item","item_key"),
                                                     "move_id": ManyToOneAttrs("move","move_key")}})
    __table_args__ = (
        #UniqueConstraint("poke_api_id",name="ux_Machine_PokeApiId"),
        UniqueConstraint("move_key","item_key","version_group_key",name="ux_Machine_move_item_version"),
    )

    """ @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["Machine"]:
        machines = []
        for id_, machine_data in df.iterrows():
            poke_api_id = id_
            machine = cls(poke_api_id=poke_api_id)
            cls._cache[machine.poke_api_id] = machine
            machines.append(machine)
        return machines """
    
    """ @classmethod
    def parse_data(cls,data) -> "Machine":
        poke_api_id = data.id_

        machine = cls(poke_api_id=poke_api_id)
        cls._cache[machine.poke_api_id] = machine
        return machine """
    
    #def __init__(self, poke_api_id: int):
    def __init__(self, data: pd.Series):
        self.id = get_next_id()
        #self.poke_api_id = poke_api_id
        self.machine_number = data.machine_number

    def compare(self, data: pd.Series):
        if self.machine_number != data.machine_number:
            self.machine_number = data.machine_number

    def get_unique_key(self):
        return str(self.version_group.poke_api_id) + ":" + str(self.item.poke_api_id) + ":" + str(self.move.poke_api_id)