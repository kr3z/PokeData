from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Computed, UniqueConstraint, Index, Boolean

from Base import Base, utf8mb4_1000, utf8mb4_200, utf8mb4_50, get_next_id, Session, PokeApiResource

if TYPE_CHECKING:
    from Berries import BerryFirmness, BerryFlavor
    from Contests import ContestType, ContestEffect, SuperContestEffect
    from Encounters import EncounterMethod, EncounterCondition, EncounterConditionValue
    from Evolution import EvolutionTrigger
    from Games import VersionGroup, Version, Generation, Pokedex
    from Pokemon import PokemonAbility, PokemonCharacteristic, PokemonSpecies
    from Pokemon import PokemonType, PokemonStat, PokemonNature, PokemonAbility
    from Pokemon import EggGroup, GrowthRate, PokemonColor, PokemonForm, PokemonHabitat
    from Pokemon import PokemonShape, PokeathlonStat
    from Moves import Move, DamageClass, PastMoveStatValues, MoveAilment, MoveBattleStyle
    from Moves import MoveCategory, MoveLearnMethod, MoveTarget
    from Items import Item, ItemAttribute, ItemFlingEffect, ItemCategory, ItemPocket
    from Locations import Location, LocationArea, PalParkArea


class Language(Base, PokeApiResource):
    __tablename__ = "Language"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(10))
    official: Mapped[bool] = mapped_column(Boolean)
    iso639: Mapped[str] = mapped_column(String(10))
    iso3166: Mapped[str] = mapped_column(String(10))

    names: Mapped[List["LanguageName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                 primaryjoin="Language.id == foreign(LanguageName.object_key)")

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Language_PokeApiId"),
    )

    _cache: Dict[int, "Language"] = {}

    @classmethod
    def parse_data(cls,data) -> "Language":
    #def parse_langauge(cls,data) -> "Language":
        poke_api_id = data.id_
        name = data.name
        official = data.official
        iso639 = data.iso639
        iso3166 = data.iso3166

        language = cls(poke_api_id=poke_api_id, name=name, official=official, iso639=iso639, iso3166=iso3166)
        cls._cache[poke_api_id] = language

        return language

    def __init__(self, poke_api_id: int, name: str, official: bool, iso639: str, iso3166: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.official = official
        self.iso639 = iso639
        self.iso3166 = iso3166

        #self.names: List["LanguageName"] = []

    def compare(self, data):
        # This should never change
        #if self.poke_api_id != data.id_:
        #    self.poke_api_id = data.id_
        if self.name != data.name:
            self.name = data.name
        if self.official != data.official:
            self.official = data.official
        if self.iso639 != data.iso639:
            self.iso639 = data.iso639
        if self.iso3166 != data.iso3166:
            self.iso3166 = data.iso3166

###################################
####### Base TextEntry table ######
###################################
class TextEntry(Base):
    __tablename__ = "TextEntry"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    type: Mapped[str] = mapped_column(String(30))
    language_key: Mapped[int] = mapped_column(Integer)

    language: Mapped["Language"] = relationship(primaryjoin="TextEntry.language_key == Language.id",
                                                foreign_keys=language_key, cascade="save-update")
    text_entry: Mapped[str] = mapped_column(utf8mb4_1000)

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_abstract": True
    }

    def __init__(self, data):
        self.id = get_next_id()

###################################
########## Abstract types #########
###################################
class VersionGroupTextEntry(TextEntry):
    version_group_key: Mapped[int] = mapped_column(Integer, nullable=True)
    version_group: Mapped["VersionGroup"] = relationship(primaryjoin="VersionGroupTextEntry.version_group_key == VersionGroup.id",
                                                        foreign_keys=version_group_key, cascade="save-update")
    __mapper_args__ = {"polymorphic_abstract": True}

    def __init__(self, data):
        super().__init__(data)

class VersionTextEntry(TextEntry):
    version_key: Mapped[int] = mapped_column(Integer, nullable=True)
    version: Mapped["Version"] = relationship(primaryjoin="VersionTextEntry.version_key == Version.id",
                                                foreign_keys=version_key, cascade="save-update")
    __mapper_args__ = {"polymorphic_abstract": True}

    def __init__(self, data):
        super().__init__(data)

class VerboseEffect(TextEntry):
    short_effect: Mapped[str] = mapped_column(utf8mb4_200, nullable=True)
    __mapper_args__ = {"polymorphic_abstract": True}
    #text_entry_name = "effect"

    def __init__(self, data):
        super().__init__(data)
        self.short_effect = data.short_effect

""" class Effect(TextEntry):
    text_entry_name = "effect"
    __mapper_args__ = {"polymorphic_abstract": True}
    def __init__(self, data):
        super().__init__(data)

class FlavorText(VersionTextEntry):
    text_entry_name = "flavor_text"
    __mapper_args__ = {"polymorphic_abstract": True}
    def __init__(self, data):
        super().__init__(data)

class Name(TextEntry):
    text_entry_name = "name"
    __mapper_args__ = {"polymorphic_abstract": True}
    def __init__(self, data):
        super().__init__(data)

class VersionGroupFlavorText(VersionGroupTextEntry):
    text_entry_name = "text"
    __mapper_args__ = {"polymorphic_abstract": True}
    def __init__(self, data):
        super().__init__(data) """



class LanguageName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer)
    object_ref: Mapped["Language"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="LanguageName.object_key == Language.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "LanguageName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name
        

###################################
####### Pokemon Text Entries ######
###################################
class AbilityEffectChange(VersionGroupTextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonAbility"] = relationship(back_populates="effect_changes", cascade="save-update",
                                            primaryjoin="AbilityEffectChange.object_key == PokemonAbility.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "AbilityEffectChange"}
    text_entry_name = "effect"

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

class AbilityFlavorText(VersionGroupTextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonAbility"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                            primaryjoin="AbilityFlavorText.object_key == PokemonAbility.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "AbilityFlavorText"}
    text_entry_name = "flavor_text"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.flavor_text

class AbilityEffect(VerboseEffect):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonAbility"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="AbilityEffect.object_key == PokemonAbility.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "AbilityEffect"}
    text_entry_name = "effect"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

class CharacteristicDescription(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonCharacteristic"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="CharacteristicDescription.object_key == PokemonCharacteristic.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "CharacteristicDescription"}
    text_entry_name = "description"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

class PokemonName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonSpecies"] = relationship(back_populates="names", cascade="save-update",
                                                        primaryjoin="PokemonName.object_key == PokemonSpecies.id",
                                                        foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class PokemonSpeciesFlavorText(VersionTextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonSpecies"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                                        primaryjoin="PokemonSpeciesFlavorText.object_key == PokemonSpecies.id",
                                                        foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonSpeciesFlavorText"}
    text_entry_name = "flavor_text"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.flavor_text

class PokemonFormDescription(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonSpecies"] = relationship(back_populates="form_descriptions", cascade="save-update",
                                                        primaryjoin="PokemonFormDescription.object_key == PokemonSpecies.id",
                                                        foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonFormDescription"}
    text_entry_name = "description"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

class PokemonGenus(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonSpecies"] = relationship(back_populates="genera", cascade="save-update",
                                                        primaryjoin="PokemonGenus.object_key == PokemonSpecies.id",
                                                        foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonGenus"}
    text_entry_name = "genus"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.genus

class PokemonTypeName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonType"] = relationship(back_populates="names", cascade="save-update",
                                                        primaryjoin="PokemonTypeName.object_key == PokemonType.id",
                                                        foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonTypeName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class PokemonStatName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonStat"] = relationship(back_populates="names", cascade="save-update",
                                                        primaryjoin="PokemonStatName.object_key == PokemonStat.id",
                                                        foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonStatName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class PokeathlonStatName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokeathlonStat"] = relationship(back_populates="names", cascade="save-update",
                                                        primaryjoin="PokeathlonStatName.object_key == PokeathlonStat.id",
                                                        foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokeathlonStatName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class PokemonNatureName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonNature"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonNatureName.object_key == PokemonNature.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonNatureName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class PokemonAbilityName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonAbility"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonAbilityName.object_key == PokemonAbility.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonAbilityName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class EggGroupName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["EggGroup"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="EggGroupName.object_key == EggGroup.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "EggGroupName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class GrowthRateDescription(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["GrowthRate"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="GrowthRateDescription.object_key == GrowthRate.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "GrowthRateDescription"}
    text_entry_name = "description"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

class PokemonColorName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonColor"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonColorName.object_key == PokemonColor.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonColorName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class PokemonFormName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonForm"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonFormName.object_key == PokemonForm.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonFormName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class PokemonFormFormName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonForm"] = relationship(back_populates="form_names", cascade="save-update",
                                            primaryjoin="PokemonFormFormName.object_key == PokemonForm.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonFormFormName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class PokemonHabitatName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonHabitat"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonHabitatName.object_key == PokemonHabitat.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonHabitatName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class PokemonShapeAwesomeName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonShape"] = relationship(back_populates="awesome_names", cascade="save-update",
                                            primaryjoin="PokemonShapeAwesomeName.object_key == PokemonShape.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonShapeAwesomeName"}
    text_entry_name = "awesome_name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.awesome_name

class PokemonShapeName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonShape"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonShapeName.object_key == PokemonShape.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokemonShapeName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

#######################
### Move Text Types ###
#######################
class MoveEffectChange(VersionGroupTextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Move"] = relationship(back_populates="effect_changes", cascade="save-update",
                                            primaryjoin="MoveEffectChange.object_key == Move.id",
                                            foreign_keys=object_key)
    #effect: Mapped[str] = mapped_column(String(200),nullable=True)
    __mapper_args__ = {"polymorphic_identity": "MoveEffectChange"}
    text_entry_name = "effect"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

class MoveFlavorText(VersionGroupTextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Move"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                            primaryjoin="MoveFlavorText.object_key == Move.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "MoveFlavorText"}
    text_entry_name = "flavor_text"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.flavor_text

class MoveEffect(VerboseEffect):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Move"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="MoveEffect.object_key == Move.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "MoveEffect"}
    text_entry_name = "effect"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

class MoveName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Move"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="MoveName.object_key == Move.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "MoveName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class PastMoveEffect(VerboseEffect):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PastMoveStatValues"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="PastMoveEffect.object_key == PastMoveStatValues.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PastMoveEffect"}
    text_entry_name = "effect"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

class MoveAilmentName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveAilment"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="MoveAilmentName.object_key == MoveAilment.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "MoveAilmentName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class MoveBattleStyleName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveBattleStyle"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="MoveBattleStyleName.object_key == MoveBattleStyle.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "MoveBattleStyleName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class MoveCategoryDescription(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveCategory"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="MoveCategoryDescription.object_key == MoveCategory.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "MoveCategoryDescription"}
    text_entry_name = "description"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

class DamageClassName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["DamageClass"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="DamageClassName.object_key == DamageClass.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "DamageClassName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class DamageClassDescription(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["DamageClass"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="DamageClassDescription.object_key == DamageClass.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "DamageClassDescription"}
    text_entry_name = "description"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

class MoveLearnMethodName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveLearnMethod"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="MoveLearnMethodName.object_key == MoveLearnMethod.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "MoveLearnMethodName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class MoveLearnMethodDescription(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveLearnMethod"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="MoveLearnMethodDescription.object_key == MoveLearnMethod.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "MoveLearnMethodDescription"}
    text_entry_name = "description"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

class MoveTargetDescription(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveTarget"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="MoveTargetDescription.object_key == MoveTarget.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "MoveTargetDescription"}
    text_entry_name = "description"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

class MoveTargetName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveTarget"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="MoveTargetName.object_key == MoveTarget.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "MoveTargetName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

###################################
###### Location Text Entries #####
###################################
class LocationName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Location"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="LocationName.object_key == Location.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "LocationName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class LocationAreaName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["LocationArea"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="LocationAreaName.object_key == LocationArea.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "LocationAreaName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class PalParkAreaName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PalParkArea"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PalParkAreaName.object_key == PalParkArea.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PalParkAreaName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

###################################
######## Item Text Entries ########
###################################
class ItemFlavorText(VersionGroupTextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Item"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                            primaryjoin="ItemFlavorText.object_key == Item.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "ItemFlavorText"}
    text_entry_name = "text"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.flavor_text

class ItemEffect(VerboseEffect):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Item"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="ItemEffect.object_key == Item.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "ItemEffect"}
    text_entry_name = "effect"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

class ItemName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Item"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ItemName.object_key == Item.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "ItemName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class ItemAttributeName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemAttribute"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ItemAttributeName.object_key == ItemAttribute.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "ItemAttributeName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class ItemAttributeDescription(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemAttribute"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ItemAttributeDescription.object_key == ItemAttribute.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "ItemAttributeDescription"}
    text_entry_name = "description"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

class ItemCategoryName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemCategory"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ItemCategoryName.object_key == ItemCategory.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "ItemCategoryName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class ItemFlingEffectEffect(VerboseEffect):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemFlingEffect"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="ItemFlingEffectEffect.object_key == ItemFlingEffect.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "ItemFlingEffectEffect"}
    text_entry_name = "effect"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

class ItemFlingEffectName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemFlingEffect"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ItemFlingEffectName.object_key == ItemFlingEffect.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "ItemFlingEffectName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class ItemPocketName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemPocket"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ItemPocketName.object_key == ItemPocket.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "ItemPocketName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

####################################
###### Evolution Text Entries ######
####################################
class EvolutionTriggerName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["EvolutionTrigger"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="EvolutionTriggerName.object_key == EvolutionTrigger.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "EvolutionTriggerName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

###################################
##### Encounter Text Entries ######
###################################
class EncounterMethodName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["EncounterMethod"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="EncounterMethodName.object_key == EncounterMethod.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "EncounterMethodName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class EncounterConditionName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["EncounterCondition"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="EncounterConditionName.object_key == EncounterCondition.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "EncounterConditionName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class EncounterConditionValueName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["EncounterConditionValue"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="EncounterConditionValueName.object_key == EncounterConditionValue.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "EncounterConditionValueName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

###################################
####### Contest Text Entries ######
###################################

class ContestName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ContestType"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ContestName.object_key == ContestType.id",
                                            foreign_keys=object_key)
    color: Mapped[str] = mapped_column(utf8mb4_50, nullable=True)
    __mapper_args__ = {"polymorphic_identity": "ContestName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name
        self.color = data.color

class ContestEffectEffect(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ContestEffect"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="ContestEffectEffect.object_key == ContestEffect.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "ContestEffectEffect"}
    text_entry_name = "effect"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

class ContestEffectFlavorText(VersionGroupTextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ContestEffect"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                            primaryjoin="ContestEffectFlavorText.object_key == ContestEffect.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "ContestEffectFlavorText"}
    text_entry_name = "flavor_text"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.flavor_text

class SuperContestEffectFlavorText(VersionGroupTextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["SuperContestEffect"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                            primaryjoin="SuperContestEffectFlavorText.object_key == SuperContestEffect.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "SuperContestEffectFlavorText"}
    text_entry_name = "flavor_text"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.flavor_text

###################################
####### Berry Text Entries #######
###################################
class BerryFirmnessName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["BerryFirmness"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="BerryFirmnessName.object_key == BerryFirmness.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "BerryFirmnessName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class BerryFlavorName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["BerryFlavor"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="BerryFlavorName.object_key == BerryFlavor.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "BerryFlavorName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

###################################
####### Games Text Entries #######
###################################
class PokedexDescription(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Pokedex"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="PokedexDescription.object_key == Pokedex.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokedexDescription"}
    text_entry_name = "description"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

class PokedexName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Pokedex"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokedexName.object_key == Pokedex.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "PokedexName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class VersionName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Version"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="VersionName.object_key == Version.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "VersionName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

class GenerationName(TextEntry):
    object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Generation"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="GenerationName.object_key == Generation.id",
                                            foreign_keys=object_key)
    __mapper_args__ = {"polymorphic_identity": "GenerationName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name