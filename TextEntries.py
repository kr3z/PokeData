import pandas as pd
from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Computed, UniqueConstraint, Index, Boolean, inspect

from Base import Base, utf8mb4_5000, utf8mb4_2500, utf8mb4_1000, utf8mb4_500, utf8mb4_50, get_next_id, Session, PokeApiResource, TinyInteger, ManyToOneAttrs, CSVData, CSVResource

if TYPE_CHECKING:
    from Berries import BerryFirmness, BerryFlavor
    from Contests import ContestType, ContestEffect, SuperContestEffect
    from Encounters import EncounterMethod, EncounterCondition, EncounterConditionValue
    from Evolution import EvolutionTrigger
    from Games import VersionGroup, Version, Generation, Pokedex
    from Pokemon import PokemonAbility, PokemonCharacteristic, PokemonSpecies
    from Pokemon import PokemonType, PokemonStat, PokemonNature, PokemonAbility
    from Pokemon import EggGroup, GrowthRate, PokemonColor, PokemonForm, PokemonHabitat
    from Pokemon import PokemonShape, PokeathlonStat, PokemonAbilityPastEffect
    from Moves import Move, DamageClass, MoveAilment, MoveBattleStyle, MoveEffect, MoveEffectChange
    from Moves import MoveCategory, MoveLearnMethod, MoveTarget
    from Items import Item, ItemAttribute, ItemFlingEffect, ItemCategory, ItemPocket
    from Locations import Location, LocationArea, PalParkArea, Region


class Language(Base, PokeApiResource):
    __tablename__ = "Language"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(10))
    official: Mapped[bool] = mapped_column(Boolean)
    iso639: Mapped[str] = mapped_column(String(10))
    iso3166: Mapped[str] = mapped_column(String(10))
    order: Mapped[Optional[int]] = mapped_column(TinyInteger)

    names: Mapped[List["LanguageName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                 primaryjoin="Language.id == foreign(LanguageName.object_key)")

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Language_PokeApiId"),
    )

    _cache: Dict[int, "Language"] = {}
    #_csv = "languages.csv"
    #relationship_attr_map = {}
    csv_data: CSVData = CSVData(**{"primary_csv": "languages.csv", "relationships": {}})

    @classmethod
    def parse_csv(cls, df: pd.DataFrame) -> List["Language"]:
        languages = []
        for id_, data in df.iterrows():
            poke_api_id = id_
            name = data.identifier
            official = data.official
            iso639 = data.iso639
            iso3166 = data.iso3166
            order = data.order
            language = cls(poke_api_id=poke_api_id, name=name, official=official, iso639=iso639, iso3166=iso3166, order=order)
            cls._cache[language.poke_api_id] = language
            languages.append(language)
        return languages

    """ @classmethod
    def parse_data(cls,data) -> "Language":
    #def parse_langauge(cls,data) -> "Language":
        poke_api_id = data.id_
        name = data.name
        official = data.official
        iso639 = data.iso639
        iso3166 = data.iso3166

        language = cls(poke_api_id=poke_api_id, name=name, official=official, iso639=iso639, iso3166=iso3166)
        cls._cache[poke_api_id] = language

        return language """

    def __init__(self, poke_api_id: int, name: str, official: bool, iso639: str, iso3166: str, order: int):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.official = official
        self.iso639 = iso639
        self.iso3166 = iso3166
        self.order = order

    """ def compare(self, data):
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
            self.iso3166 = data.iso3166 """

    def compare(self, data: pd.Series) -> bool:
        updated = False
        if self.name != data.identifier:
            self.name = data.identifier
            updated = True
        if self.official != data.official:
            self.official = data.official
            updated = True
        if self.iso639 != data.iso639:
            self.iso639 = data.iso639
            updated = True
        if self.iso3166 != data.iso3166:
            self.iso3166 = data.iso3166
            updated = True
        if self.order != data.order:
            self.order = data.order
            updated = True
        return updated


###################################
####### Base TextEntry table ######
###################################
class TextEntry(Base, CSVResource):
    __tablename__ = "TextEntry"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    object_type: Mapped[str] = mapped_column(String(30))
    object_key: Mapped[int] = mapped_column(Integer)
    language_key: Mapped[int] = mapped_column(Integer)

    language: Mapped["Language"] = relationship(primaryjoin="TextEntry.language_key == Language.id",
                                                foreign_keys=language_key, cascade="save-update")
    text_entry: Mapped[str] = mapped_column(utf8mb4_5000)

    __mapper_args__ = {
        "polymorphic_on": "object_type",
        "polymorphic_abstract": True
    }
    relationship_attr_map = {"local_language_id": ManyToOneAttrs("language","language_key")}

    def __init__(self, data):
        self.id = get_next_id()

    def get_unique_key(self):
        return str(self.language.poke_api_id)
    
    def compare(self, data):
        if data[self.text_entry_name] and self.text_entry != data[self.text_entry_name]:
            self.text_entry = data[self.text_entry_name]

###################################
########## Abstract types #########
###################################
class VersionGroupTextEntry(TextEntry):
    version_group_key: Mapped[int] = mapped_column(Integer, nullable=True)
    version_group: Mapped["VersionGroup"] = relationship(primaryjoin="VersionGroupTextEntry.version_group_key == VersionGroup.id",
                                                        foreign_keys=version_group_key, cascade="save-update")
    __mapper_args__ = {"polymorphic_abstract": True}
    # Uses language_id instead of local_language_id
    #relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map = {"language_id": ManyToOneAttrs("language","language_key")}
    relationship_attr_map.update({"version_group_id": ManyToOneAttrs("version_group","version_group_key")})

    def __init__(self, data):
        super().__init__(data)

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.version_group.poke_api_id)

class NestedVersionGroupTextEntry(VersionGroupTextEntry):
    __mapper_args__ = {"polymorphic_abstract": True}
    # Uses local_language_id, unlike VersionGroupTextEntry
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"version_group_id": ManyToOneAttrs("version_group","version_group_key")})

    def __init__(self, data):
        super().__init__(data)

    def get_unique_key(self):
        return super().get_unique_key()

class VersionTextEntry(TextEntry):
    version_key: Mapped[int] = mapped_column(Integer, nullable=True)
    version: Mapped["Version"] = relationship(primaryjoin="VersionTextEntry.version_key == Version.id",
                                                foreign_keys=version_key, cascade="save-update")
    __mapper_args__ = {"polymorphic_abstract": True}
    # Uses language_id instead of local_language_id
    #relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map = {"language_id": ManyToOneAttrs("language","language_key")}
    relationship_attr_map.update({"version_id": ManyToOneAttrs("version","version_key")})

    def __init__(self, data):
        super().__init__(data)

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.version.poke_api_id)

class VerboseEffect(TextEntry):
    secondary_text_entry: Mapped[str] = mapped_column(utf8mb4_500, nullable=True)
    __mapper_args__ = {"polymorphic_abstract": True}
    #text_entry_name = "effect"

    def __init__(self, data):
        super().__init__(data)
        self.secondary_text_entry = data.short_effect

    def get_unique_key(self):
        return super().get_unique_key()
    
class SubtitledTextEntry(TextEntry):
    secondary_text_entry: Mapped[str] = mapped_column(utf8mb4_500, nullable=True, use_existing_column=True)
    __mapper_args__ = {"polymorphic_abstract": True}

    def __init__(self, data):
        super().__init__(data)
        self.secondary_text_entry = data.subtitle

    def get_unique_key(self):
        return super().get_unique_key()

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
    #object_key: Mapped[int] = mapped_column(Integer)
    object_ref: Mapped["Language"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="LanguageName.object_key == Language.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "LanguageName"}

    text_entry_name = "name"

    #_csv = "language_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"language_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "language_names.csv", "relationships": relationship_attr_map})

    """ @classmethod
    def build_text_keys(cls, data: pd.DataFrame) -> Dict[int,str]:
        idx_to_text_keys: Dict[int, str] = {}
        for idx, row_data in data.iterrows():
            text_key = str(row_data.language_id) + ":" + str(row_data.local_language_id)
            idx_to_text_keys[idx] = text_key
        return idx_to_text_keys """

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

        ins = inspect(self)
        object_class = ins.mapper.relationships.object_ref.mapper.class_
        language_class = ins.mapper.relationships.language.mapper.class_
        object_ref, _ = object_class.get_from_cache(data.language_id)
        lang_ref, _ = language_class.get_from_cache(data.local_language_id)
        self.object_ref = object_ref
        self.object_key = object_ref.id
        self.language = lang_ref
        self.language_key = lang_ref.id

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  
       

###################################
####### Pokemon Text Entries ######
###################################

class PokemonAbilityName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonAbility"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonAbilityName.object_key == PokemonAbility.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonAbilityName"}
    text_entry_name = "name"
    #_csv = "ability_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"ability_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "ability_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

""" class AbilityEffectChange(NestedVersionGroupTextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonAbility"] = relationship(back_populates="effect_changes", cascade="save-update",
                                            primaryjoin="AbilityEffectChange.object_key == PokemonAbility.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "AbilityEffectChange"}
    text_entry_name = "effect"
    nested_entry_name = "effect_entries"
    #_csv = "ability_changelog_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"ability_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "ability_changelog_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id) """

class AbilityFlavorText(VersionGroupTextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonAbility"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                            primaryjoin="AbilityFlavorText.object_key == PokemonAbility.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "AbilityFlavorText"}
    text_entry_name = "flavor_text"
    #_csv = "ability_flavor_text.csv"
    relationship_attr_map = dict(VersionGroupTextEntry.relationship_attr_map)
    relationship_attr_map.update({"ability_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "ability_flavor_text.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.flavor_text

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class AbilityEffect(VerboseEffect):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonAbility"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="AbilityEffect.object_key == PokemonAbility.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "AbilityEffect"}
    text_entry_name = "effect"
    #_csv = "ability_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"ability_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "ability_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  
    
class AbilityPastEffect(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonAbilityPastEffect"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="AbilityPastEffect.object_key == PokemonAbilityPastEffect.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "AbilityPastEffect"}
    text_entry_name = "effect"

    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"ability_changelog_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "ability_changelog_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class CharacteristicDescription(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonCharacteristic"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="CharacteristicDescription.object_key == PokemonCharacteristic.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "CharacteristicDescription"}
    #text_entry_name = "description"
    text_entry_name = "message"
    #_csv = "characteristic_tsxt.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"characteristic_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "characteristic_text.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonSpecies"] = relationship(back_populates="names", cascade="save-update",
                                                        primaryjoin="PokemonName.object_key == PokemonSpecies.id",
                                                        foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonName"}
    text_entry_name = "name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_species_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_species_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonSpeciesFlavorText(VersionTextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonSpecies"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                                        primaryjoin="PokemonSpeciesFlavorText.object_key == PokemonSpecies.id",
                                                        foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonSpeciesFlavorText"}
    text_entry_name = "flavor_text"
    relationship_attr_map = dict(VersionTextEntry.relationship_attr_map)
    relationship_attr_map.update({"species_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_species_flavor_text.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonFormDescription(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonSpecies"] = relationship(back_populates="form_descriptions", cascade="save-update",
                                                        primaryjoin="PokemonFormDescription.object_key == PokemonSpecies.id",
                                                        foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonFormDescription"}
    #text_entry_name = "description"
    text_entry_name = "form_description"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_species_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_species_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonGenus(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonSpecies"] = relationship(back_populates="genera", cascade="save-update",
                                                        primaryjoin="PokemonGenus.object_key == PokemonSpecies.id",
                                                        foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonGenus"}
    text_entry_name = "genus"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_species_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_species_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.genus
        if not self.text_entry:
            self.text_entry = ""

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonTypeName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonType"] = relationship(back_populates="names", cascade="save-update",
                                                        primaryjoin="PokemonTypeName.object_key == PokemonType.id",
                                                        foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonTypeName"}
    text_entry_name = "name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"type_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "type_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonStatName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonStat"] = relationship(back_populates="names", cascade="save-update",
                                                        primaryjoin="PokemonStatName.object_key == PokemonStat.id",
                                                        foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonStatName"}
    text_entry_name = "name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"stat_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "stat_names.csv", "relationships": relationship_attr_map})
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokeathlonStatName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokeathlonStat"] = relationship(back_populates="names", cascade="save-update",
                                                        primaryjoin="PokeathlonStatName.object_key == PokeathlonStat.id",
                                                        foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokeathlonStatName"}
    text_entry_name = "name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokeathlon_stat_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokeathlon_stat_names.csv", "relationships": relationship_attr_map})
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonNatureName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonNature"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonNatureName.object_key == PokemonNature.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonNatureName"}
    text_entry_name = "name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"nature_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "nature_names.csv", "relationships": relationship_attr_map})
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class EggGroupName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["EggGroup"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="EggGroupName.object_key == EggGroup.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "EggGroupName"}
    text_entry_name = "name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"egg_group_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "egg_group_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class GrowthRateName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["GrowthRate"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="GrowthRateName.object_key == GrowthRate.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "GrowthRateName"}
    text_entry_name = "name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"growth_rate_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "growth_rate_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.name

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  
    
""" class GrowthRateDescription(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["GrowthRate"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="GrowthRateDescription.object_key == GrowthRate.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "GrowthRateDescription"}
    text_entry_name = "description"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"growth_rate_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "growth_rate_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)   """

class PokemonColorName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonColor"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonColorName.object_key == PokemonColor.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonColorName"}
    text_entry_name = "name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_color_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_color_names.csv", "relationships": relationship_attr_map})
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonFormName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonForm"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonFormName.object_key == PokemonForm.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonFormName"}
    text_entry_name = "pokemon_name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_form_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_form_names.csv", "relationships": relationship_attr_map})
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]
        if not self.text_entry:
            self.text_entry = ""

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonFormFormName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonForm"] = relationship(back_populates="form_names", cascade="save-update",
                                            primaryjoin="PokemonFormFormName.object_key == PokemonForm.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonFormFormName"}
    text_entry_name = "form_name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_form_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_form_names.csv", "relationships": relationship_attr_map})
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]
        if not self.text_entry:
            self.text_entry = ""

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonHabitatName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonHabitat"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonHabitatName.object_key == PokemonHabitat.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonHabitatName"}
    text_entry_name = "name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_habitat_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_habitat_names.csv", "relationships": relationship_attr_map})
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonShapeAwesomeName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonShape"] = relationship(back_populates="awesome_names", cascade="save-update",
                                            primaryjoin="PokemonShapeAwesomeName.object_key == PokemonShape.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonShapeAwesomeName"}
    text_entry_name = "awesome_name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_shape_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_shape_prose.csv", "relationships": relationship_attr_map})
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokemonShapeName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonShape"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokemonShapeName.object_key == PokemonShape.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonShapeName"}
    text_entry_name = "name"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_shape_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_shape_prose.csv", "relationships": relationship_attr_map})
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  
    
class PokemonShapeDescription(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PokemonShape"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="PokemonShapeDescription.object_key == PokemonShape.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokemonShapeDescription"}
    text_entry_name = "description"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_shape_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_shape_prose.csv", "relationships": relationship_attr_map})
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

#######################
### Move Text Types ###
#######################

class MoveFlavorText(VersionGroupTextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Move"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                            primaryjoin="MoveFlavorText.object_key == Move.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "MoveFlavorText"}
    text_entry_name = "flavor_text"
    #_csv = "move_flavor_text.csv"
    relationship_attr_map = dict(VersionGroupTextEntry.relationship_attr_map)
    relationship_attr_map.update({"move_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "move_flavor_text.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.flavor_text

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class MoveName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Move"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="MoveName.object_key == Move.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "MoveName"}
    text_entry_name = "name"
    #_csv = "move_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"move_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "move_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  
    
class MoveEffectChangeText(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveEffectChange"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="MoveEffectChangeText.object_key == MoveEffectChange.id",
                                            foreign_keys="TextEntry.object_key")
    #effect: Mapped[str] = mapped_column(String(200),nullable=True)
    __mapper_args__ = {"polymorphic_identity": "MoveEffectChangeText"}
    text_entry_name = "effect"
    #nested_entry_name = "effect_entries"
    #_csv = "move_effect_changelog_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"move_effect_changelog_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "move_effect_changelog_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  
    
class MoveEffectEffect(VerboseEffect):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveEffect"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="MoveEffectEffect.object_key == MoveEffect.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "MoveEffectEffect"}
    text_entry_name = "effect"
    #_csv = "move_effect_prose.csv"
    relationship_attr_map = dict(VerboseEffect.relationship_attr_map)
    relationship_attr_map.update({"move_effect_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "move_effect_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

""" class PastMoveEffect(VerboseEffect):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PastMoveStatValues"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="PastMoveEffect.object_key == PastMoveStatValues.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PastMoveEffect"}
    text_entry_name = "effect"
    #_csv = "move_effect_changelog_prose.csv"
    relationship_attr_map = dict(VerboseEffect.relationship_attr_map)
    relationship_attr_map.update({"move_effect_changelog_id": ManyToOneAttrs("object_ref","object_key")})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  """ 

class MoveAilmentName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveAilment"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="MoveAilmentName.object_key == MoveAilment.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "MoveAilmentName"}
    text_entry_name = "name"
    #_csv = "move_meta_ailment_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"move_meta_ailment_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "move_meta_ailment_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class MoveBattleStyleName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveBattleStyle"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="MoveBattleStyleName.object_key == MoveBattleStyle.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "MoveBattleStyleName"}
    text_entry_name = "name"
    #_csv = "move_battle_style_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"move_battle_style_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "move_battle_style_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class MoveCategoryDescription(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveCategory"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="MoveCategoryDescription.object_key == MoveCategory.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "MoveCategoryDescription"}
    text_entry_name = "description"
    #_csv = "move_meta_category_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"move_meta_category_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "move_meta_category_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class DamageClassName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["DamageClass"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="DamageClassName.object_key == DamageClass.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "DamageClassName"}
    text_entry_name = "name"
    #_csv = "move_damage_class_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"move_damage_class_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "move_damage_class_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class DamageClassDescription(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["DamageClass"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="DamageClassDescription.object_key == DamageClass.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "DamageClassDescription"}
    text_entry_name = "description"
    #_csv = "move_damage_class_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"move_damage_class_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "move_damage_class_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class MoveLearnMethodName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveLearnMethod"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="MoveLearnMethodName.object_key == MoveLearnMethod.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "MoveLearnMethodName"}
    text_entry_name = "name"
    #_csv = "pokemon_move_method_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_move_method_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_move_method_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class MoveLearnMethodDescription(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveLearnMethod"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="MoveLearnMethodDescription.object_key == MoveLearnMethod.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "MoveLearnMethodDescription"}
    text_entry_name = "description"
    #_csv = "pokemon_move_method_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokemon_move_method_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokemon_move_method_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class MoveTargetDescription(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveTarget"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="MoveTargetDescription.object_key == MoveTarget.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "MoveTargetDescription"}
    text_entry_name = "description"
    #_csv = "move_target_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"move_target_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "move_target_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class MoveTargetName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["MoveTarget"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="MoveTargetName.object_key == MoveTarget.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "MoveTargetName"}
    text_entry_name = "name"
    #_csv = "move_target_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"move_target_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "move_target_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

###################################
###### Location Text Entries #####
###################################
class LocationName(SubtitledTextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Location"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="LocationName.object_key == Location.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "LocationName"}
    text_entry_name = "name"
    #_csv = "location_names.csv"
    relationship_attr_map = dict(SubtitledTextEntry.relationship_attr_map)
    relationship_attr_map.update({"location_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "location_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class LocationAreaName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["LocationArea"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="LocationAreaName.object_key == LocationArea.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "LocationAreaName"}
    text_entry_name = "name"
    #_csv = "location_area_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"location_area_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "location_area_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PalParkAreaName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["PalParkArea"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PalParkAreaName.object_key == PalParkArea.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PalParkAreaName"}
    text_entry_name = "name"
    #_csv = "pal_park_area_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pal_park_area_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pal_park_area_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  
    
class RegionName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Region"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="RegionName.object_key == Region.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "RegionName"}
    text_entry_name = "name"
    #_csv = "region_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"region_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "region_names.csv", "relationships": relationship_attr_map})

    """ @classmethod
    def build_text_keys(cls, data: pd.DataFrame) -> Dict[int,str]:
        idx_to_text_keys: Dict[int, str] = {}
        for idx, row_data in data.iterrows():
            text_key = str(row_data.region_id) + ":" + str(row_data.local_language_id)
            idx_to_text_keys[idx] = text_key
        return idx_to_text_keys """

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

        """ ins = inspect(self)
        object_class = ins.mapper.relationships.object_ref.mapper.class_
        language_class = ins.mapper.relationships.language.mapper.class_
        object_ref, _ = object_class.get_from_cache(data.region_id)
        lang_ref, _ = language_class.get_from_cache(data.local_language_id)
        self.object_ref = object_ref
        self.object_key = object_ref.id
        self.language = lang_ref
        self.language_key = lang_ref.id """

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

###################################
######## Item Text Entries ########
###################################
class ItemFlavorText(VersionGroupTextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Item"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                            primaryjoin="ItemFlavorText.object_key == Item.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "ItemFlavorText"}
    text_entry_name = "flavor_text"
    #_csv = "item_flavor_text.csv"
    relationship_attr_map = dict(VersionGroupTextEntry.relationship_attr_map)
    relationship_attr_map.update({"item_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "item_flavor_text.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.flavor_text
        if not self.text_entry:
            self.text_entry = ""

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class ItemEffect(VerboseEffect):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Item"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="ItemEffect.object_key == Item.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "ItemEffect"}
    text_entry_name = "effect"
    #_csv = "item_prose.csv"
    relationship_attr_map = dict(VerboseEffect.relationship_attr_map)
    relationship_attr_map.update({"item_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "item_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect
        if not self.text_entry:
            self.text_entry = ""

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class ItemName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Item"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ItemName.object_key == Item.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "ItemName"}
    text_entry_name = "name"
    #_csv = "item_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"item_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "item_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class ItemAttributeName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemAttribute"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ItemAttributeName.object_key == ItemAttribute.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "ItemAttributeName"}
    text_entry_name = "name"
    #_csv = "item_flag_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"item_flag_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "item_flag_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class ItemAttributeDescription(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemAttribute"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="ItemAttributeDescription.object_key == ItemAttribute.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "ItemAttributeDescription"}
    text_entry_name = "description"
    #_csv = "item_flag_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"item_flag_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "item_flag_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class ItemCategoryName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemCategory"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ItemCategoryName.object_key == ItemCategory.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "ItemCategoryName"}
    text_entry_name = "name"
    #_csv = "item_category_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"item_category_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "item_category_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class ItemFlingEffectEffect(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemFlingEffect"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="ItemFlingEffectEffect.object_key == ItemFlingEffect.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "ItemFlingEffectEffect"}
    text_entry_name = "effect"
    #_csv = "item_fling_effect_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"item_fling_effect_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "item_fling_effect_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

""" class ItemFlingEffectName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemFlingEffect"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ItemFlingEffectName.object_key == ItemFlingEffect.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "ItemFlingEffectName"}
    text_entry_name = "name"
    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name] """

class ItemPocketName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ItemPocket"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ItemPocketName.object_key == ItemPocket.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "ItemPocketName"}
    text_entry_name = "name"
    #_csv = "item_pocket_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"item_pocket_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "item_pocket_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

####################################
###### Evolution Text Entries ######
####################################
class EvolutionTriggerName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["EvolutionTrigger"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="EvolutionTriggerName.object_key == EvolutionTrigger.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "EvolutionTriggerName"}
    text_entry_name = "name"
    #_csv = "evolution_trigger_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"evolution_trigger_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "evolution_trigger_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

###################################
##### Encounter Text Entries ######
###################################
class EncounterMethodName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["EncounterMethod"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="EncounterMethodName.object_key == EncounterMethod.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "EncounterMethodName"}
    text_entry_name = "name"
    #_csv = "encounter_method_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"encounter_method_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "encounter_method_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class EncounterConditionName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["EncounterCondition"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="EncounterConditionName.object_key == EncounterCondition.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "EncounterConditionName"}
    text_entry_name = "name"
    #_csv = "encounter_condition_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"encounter_condition_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "encounter_condition_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class EncounterConditionValueName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["EncounterConditionValue"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="EncounterConditionValueName.object_key == EncounterConditionValue.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "EncounterConditionValueName"}
    text_entry_name = "name"
    #_csv = "encounter_condition_value_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"encounter_condition_value_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "encounter_condition_value_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

###################################
####### Contest Text Entries ######
###################################

class ContestName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ContestType"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="ContestName.object_key == ContestType.id",
                                            foreign_keys="TextEntry.object_key")
    color: Mapped[str] = mapped_column(utf8mb4_50, nullable=True)
    __mapper_args__ = {"polymorphic_identity": "ContestName"}
    text_entry_name = "name"
    #_csv = "contest_type_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"contest_type_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "contest_type_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]
        self.color = data.color

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  
    
    def compare(self, data) -> bool:
        updated = False
        if self.text_entry != data[self.text_entry_name]:
            self.text_entry = data[self.text_entry_name]
            updated = True
        if self.color != data.color:
            self.color = data.color
            updated = True
        return updated

class ContestEffectEffect(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ContestEffect"] = relationship(back_populates="effect_entries", cascade="save-update",
                                            primaryjoin="ContestEffectEffect.object_key == ContestEffect.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "ContestEffectEffect"}
    text_entry_name = "effect"
    #_csv = "contest_effect_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"contest_effect_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "contest_effect_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.effect

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class ContestEffectFlavorText(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ContestEffect"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                            primaryjoin="ContestEffectFlavorText.object_key == ContestEffect.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "ContestEffectFlavorText"}
    text_entry_name = "flavor_text"
    #_csv = "contest_effect_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"contest_effect_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "contest_effect_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.flavor_text

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class SuperContestEffectFlavorText(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["SuperContestEffect"] = relationship(back_populates="flavor_text_entries", cascade="save-update",
                                            primaryjoin="SuperContestEffectFlavorText.object_key == SuperContestEffect.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "SuperContestEffectFlavorText"}
    text_entry_name = "flavor_text"
    #_csv = "super_contest_effect_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"super_contest_effect_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "super_contest_effect_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.flavor_text

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

###################################
####### Berry Text Entries #######
###################################
class BerryFirmnessName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["BerryFirmness"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="BerryFirmnessName.object_key == BerryFirmness.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "BerryFirmnessName"}
    text_entry_name = "name"
    #_csv = "berry_firmness_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"berry_firmness_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "berry_firmness_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class BerryFlavorName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["ContestType"] = relationship(back_populates="flavors", cascade="save-update",
                                            primaryjoin="BerryFlavorName.object_key == ContestType.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "BerryFlavorName"}
    #text_entry_name = "name"
    text_entry_name = "flavor"
    ### !!! No CSV !!!
    ### oh wait, its in contest_type_names, but as flavor
    #_csv = "contest_type_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"contest_type_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "contest_type_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

###################################
####### Games Text Entries #######
###################################
class PokedexDescription(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Pokedex"] = relationship(back_populates="descriptions", cascade="save-update",
                                            primaryjoin="PokedexDescription.object_key == Pokedex.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokedexDescription"}
    text_entry_name = "description"
    #_csv = "pokedex_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokedex_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokedex_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data.description
        if not self.text_entry:
            self.text_entry = ""

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class PokedexName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Pokedex"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="PokedexName.object_key == Pokedex.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "PokedexName"}
    text_entry_name = "name"
    #_csv = "pokedex_prose.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"pokedex_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "pokedex_prose.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class VersionName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Version"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="VersionName.object_key == Version.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "VersionName"}
    text_entry_name = "name"
    #_csv = "version_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"version_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "version_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  

class GenerationName(TextEntry):
    #object_key: Mapped[int] = mapped_column(Integer,use_existing_column=True)
    object_ref: Mapped["Generation"] = relationship(back_populates="names", cascade="save-update",
                                            primaryjoin="GenerationName.object_key == Generation.id",
                                            foreign_keys="TextEntry.object_key")
    __mapper_args__ = {"polymorphic_identity": "GenerationName"}
    text_entry_name = "name"
    #_csv = "generation_names.csv"
    relationship_attr_map = dict(TextEntry.relationship_attr_map)
    relationship_attr_map.update({"generation_id": ManyToOneAttrs("object_ref","object_key")})
    csv_data: CSVData = CSVData(**{"primary_csv": "generation_names.csv", "relationships": relationship_attr_map})

    def __init__(self, data):
        super().__init__(data)
        self.text_entry = data[self.text_entry_name]

    def get_unique_key(self):
        text_key = super().get_unique_key()
        return text_key + ":" + str(self.object_ref.poke_api_id)  