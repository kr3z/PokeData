import logging
import pandas as pd
import numpy as np
from typing import Type, Dict, List
from sqlalchemy import select, inspect, delete

from Base import Session, PokeApiResource, WORKING_DIR, ManyToOneAttrs, CSVResource, FilterOperation
from Berries import Berry, BerryFlavor, BerryFirmness
from Contests import ContestType, ContestEffect, SuperContestEffect
from Evolution import EvolutionChain, ChainLink, EvolutionDetail, EvolutionTrigger
from Encounters import Encounter, EncounterMethod, EncounterCondition, EncounterConditionValue
from Games import Generation, GenerationGameIndex, VersionGroup, Pokedex, VersionGameIndex, Version, PokedexEntry, GameIndex
from Items import Item, ItemAttribute, ItemCategory, ItemFlingEffect, ItemPocket
from Locations import Region, Location, PalParkEncounter, PalParkArea, PokemonEncounter, LocationArea, EncounterMethodRate
from Moves import Move, MoveLearnMethod, Machine, MoveBattleStyle, DamageClass, MoveTarget, MoveCategory, MoveStatChange, PastMoveStatValues, MoveAilment
from Pokemon import Pokemon, PokemonSpecies, EggGroup, PokemonColor, PokemonShape, PokemonHabitat, PokemonStat, PokemonNature, MoveBattleStylePreference, PokeathlonStat, PokemonType, PokemonTypeRelation
from Pokemon import PastTypeLink, PokemonAbility, PokemonForm, GrowthRate, GrowthRateExperienceLevel, PokemonCharacteristic, PokemonHeldItem, PokemonMove
from TextEntries import Language, TextEntry, VersionTextEntry, VersionGroupTextEntry, NestedVersionGroupTextEntry

logger = logging.getLogger('pokeapi')
CSV_DIR = WORKING_DIR + "/pokeapi/data/v2/csv/"

""" languages_df = pd.read_csv(CSV_DIR+'languages.csv', index_col='id')
languages_df = languages_df.replace({np.nan: None})

regions_df = pd.read_csv(CSV_DIR+'regions.csv', index_col='id')
regions_df = regions_df.replace({np.nan: None}) """

### !!! Need to check move flags, doesn't seem to exist in the API, but does in csv


### Process Order:
### Load Language first as all TextEntry types will depend on it
### TextEntry types can be loaded anytime after their respective type
# Language LanguageName

### Then load Region/Generation/VersionGroup/Version
### as some TextEntries will depend on VersionGroup/Version
# Region RegionName
# Generation GenerationName
# VersionGroup
## Need to process version_group_regions.csv
# Version VersionName (version_names.csv has error, introduced in most recent commit, hopefully fixed soon)

### After that we can load any types without links
### Or that only link to Region/Generation/VersionGroup/Version
# BerryFirmness
# ContestType ContestName BerryFlavorName
# ContestEffect ContestEffectEffect ContestEffectFlavorText
# SuperContestEffect SuperContestEffectFlavorText
# ItemAttribute ItemAttributeName ItemAttributeDescription
# ItemFlingEffect ItemFlingEffectEffect
# ItemPocket ItemPocketName
# Location LocationName (depends on Region)
# PalParkArea PalParkAreaName
# MoveEffect MoveEffectEffect
# MoveAilment MoveAilmentName
# MoveBattleStyle MoveBattleStyleName
# MoveCategory MoveCategoryDescription
# DamageClass DamageClassName DamageClassDescription
# MoveLearnMethod (pokemon_move_methods.csv) MoveLearnMethodName MoveLearnMethodDescription
# MoveTarget MoveTargetName MoveTargetDescription
# PokeathlonStat PokeathlonStatName
# PokemonColor PokemonColorName
# PokemonHabitat PokemonHabitatName
# PokemonShape PokemonShapeName PokemonShapeAwesomName PokemonShapeDescription

# Pokedex PokedexName PokedexDescription # Region
# PokemonType PokemonTypeName # Generation/DamageClass
# PokemonTypeRelation # PokemonType/Generation
# PokemonStat PokemonStatName # Depends on DamageClass

# LocationArea LocationAreaName # depends on location

# MoveEffectChange MoveEffectChangeText # Depends on MoveEffect
# Move MoveName # Depends on Generation/Type/MoveEffect/MoveTarget/DamageClass/ContestType/ContestEffect/SuperContestEffect

## PastMoveStatValues depends on Move/VersionGroup/Type and is not APIResource
## MoveStatChange depends on Move/Stat and is not APIResource

# BerryFlavor # Berry ContestType

# EncounterMethodRate # depends on LocationArea/EncounterMethod/Version

### Process Game Index Types:
# TypeGameIndex # depends on Type/Generation
# LocationGameIndex # depends on Location/Generation


def process_nonapi_csv(T: Type[CSVResource]):
    type_name = T.__tablename__
    CSV = CSV_DIR + T.csv_data['primary_csv']
    logger.debug("Process non-api CSV file for %s at location: %s", type_name, CSV)
    df = pd.read_csv(CSV)
    if T.csv_data.get("concat_csvs"):
        for csv_file in T.csv_data.get("concat_csvs"):
            df2 = pd.read_csv(CSV_DIR + csv_file)
            #df2.rename(columns={merge_column: 'id'}, inplace=True)
            df = pd.concat([df, df2], ignore_index=True, sort=False)
            #df.set_index('id', inplace=True)
    df = df.replace({np.nan: None})

    with Session() as session:
        existing_entries = session.scalars(select(T)).all()
        existing_entry_map: Dict[str, CSVResource] = { existing_entry.get_unique_key(): existing_entry for existing_entry in existing_entries}
    if len(existing_entry_map) > 0:
        logger.debug("Process %s: Found %s existing entries for %s", type_name, len(existing_entry_map), type_name)
    
    idx_to_keys: Dict[int, str] = {}
    for idx,row_data in df.iterrows():
        unique_key = ":".join([str(int(row_data[attr_name])) if isinstance(row_data[attr_name],float) else str(row_data[attr_name]) for attr_name in T.csv_data['relationships'].keys()])
        idx_to_keys[idx] = unique_key

    new_idxs = []
    #updated_entries = []
    update_entries_map: Dict[CSVResource, pd.Series] = {}
    for idx, unique_key in idx_to_keys.items():
        existing_entry = existing_entry_map.pop(unique_key, None)
        if existing_entry:
            """ if existing_entry.compare(df.loc[idx]):
                updated_entries.append(existing_entry) """
            update_entries_map[existing_entry] = df.loc[idx]
        else:
            logger.debug("Process %s: Parsing new entry: %s", type_name, unique_key)
            new_idxs.append(idx)

    with Session() as session:
        for existing_object, object_data in update_entries_map.items():
            existing_object = session.merge(existing_object)
            #object_data = df.loc[api_object.poke_api_id]
            existing_object.compare(object_data)
            logger.debug("Process %s: Parsing ManyToOnes for existing object: %s", type_name, existing_object)
            process_many_to_one(existing_object, object_data)
            session.flush()
        session.commit()

    with Session() as session:
        for idx,entry_data in df.loc[new_idxs].iterrows():
            new_object: CSVResource = T(entry_data)
            logger.debug("Process %s: Parsing ManyToOnes for new object: %s", type_name, new_object)
            process_many_to_one(new_object, entry_data)
            new_object = session.merge(new_object)

        session.flush()
        """for updated_entry in updated_entries:
            updated_entry = session.merge(updated_entry)
        session.flush() """

        if len(existing_entry_map) > 0:
            logger.debug("Process %s: Found %s existing entries to be deleted for %s", type_name, len(existing_entry_map), type_name)
            for entry_to_delete in existing_entry_map:
                logger.debug("Process %s: Deleting entry: %s", type_name, entry_to_delete)
            ids_to_delete: List[int] = [ delete_entry.id for delete_entry in existing_entry_map.values() ]
            session.execute(delete(T).where(T.id.in_(ids_to_delete)))
        session.commit()

def process_text_entry_csv(T: Type[TextEntry]):
    type_name = T.__tablename__
    CSV = CSV_DIR + T.csv_data['primary_csv']
    logger.debug("Process text entry CSV file for %s at location: %s", type_name, CSV)
    df = pd.read_csv(CSV)
    df = df.replace({np.nan: None})

    with Session() as session:
        existing_entries = session.scalars(select(T)).all()
        text_entry_map: Dict[str, TextEntry] = { text_entry.get_text_key(): text_entry for text_entry in existing_entries}
    if len(text_entry_map) > 0:
        logger.debug("Process %s: Found %s existing TextEntries for %s", type_name, len(text_entry_map), type_name)
    #idx_to_text_keys: Dict[int, str] = T.build_text_keys(df)
    idx_to_text_keys: Dict[int, str] = {}
    for idx,row_data in df.iterrows():
        text_key = ":".join([str(row_data[attr_name]) for attr_name in T.csv_data['relationships'].keys()])
        idx_to_text_keys[idx] = text_key
    new_idxs = []
    updated_entries = []
    for idx, text_key in idx_to_text_keys.items():
        text_entry = text_entry_map.pop(text_key, None)
        if text_entry:
            #logger.debug("Process %s: Found existing TextEntry for key: %s", type_name, text_key)
            if text_entry.compare(df.loc[idx]):
                updated_entries.append(text_entry)
        else:
            logger.debug("Process %s: Parsing new TextEntry: %s", type_name, text_key)
            new_idxs.append(idx)
    with Session() as session:
        for idx,text_data in df.loc[new_idxs].iterrows():
            text_object: TextEntry = T(text_data)
            process_many_to_one(text_object, text_data)
            text_object = session.merge(text_object)


            """ ins = inspect(text_object)
            for data_attr_name,object_attr_names  in T.relationship_attr_map.items():
                data_id = text_data[data_attr_name]
                object_class = getattr(ins.mapper.relationships,object_attr_names[0]).mapper.class_
                object_ref, _ = object_class.get_from_cache(data_id)
                setattr(text_object,object_attr_names[0],object_ref)
                setattr(text_object,object_attr_names[1],object_ref.id) """

        session.flush()
        for text_entry in updated_entries:
            text_entry = session.merge(text_entry)
        session.flush()

        if len(text_entry_map) > 0:
            logger.debug("Process %s: Found %s existing TextEntries to be deleted for %s", type_name, len(text_entry_map), type_name)
            for text_to_delete in text_entry_map:
                logger.debug("Process %s: Deleting TextEntry: %s", type_name, text_to_delete)
            text_ids_to_delete: List[int] = [ text_entry.id for text_entry in text_entry_map.values() ]
            session.execute(delete(T).where(T.id.in_(text_ids_to_delete)))
        session.commit()

#def process_game_index_csv(T: Type[GameIndex]):

            

def process_csv(T: Type[PokeApiResource]):
    type_name = T.__tablename__
    CSV = CSV_DIR + T.csv_data['primary_csv']
    logger.debug("Process CSV file for %s at location: %s", type_name, CSV)
    new_pokeapi_ids = []
    objects_to_update = []
    df = pd.read_csv(CSV, index_col='id')
    #if T.csv_data.get("merge_csvs"):
    for merge_csv in T.csv_data.merge_csvs:
        #for csv_file, merge_column in T.csv_data.get("merge_csvs").items():
            df2 = pd.read_csv(CSV_DIR + merge_csv.csv)
            if merge_csv.filter:
                filter = merge_csv.filter
                filter_att = getattr(df2, filter.column_name)
                if filter.operation == FilterOperation.GREATERTHAN:
                    df2 = df2[filter_att > filter.value]
                elif filter.operation == FilterOperation.LESSTHAN:
                    df2 = df2[filter_att < filter.value]
                elif filter.operation == FilterOperation.EQUAL:
                    df2 = df2[filter_att == filter.value]

            rename_cols = {merge_csv.merge_column: 'id'}
            if merge_csv.rename_columns:
                rename_cols.update(merge_csv.rename_columns)
            df2.rename(columns=rename_cols, inplace=True)

            df = pd.merge(df, df2, how="left", on="id")
            df.set_index('id', inplace=True)
            
    df = df.replace({np.nan: None})
    for pokeapi_id in df.index.to_list():
        api_object, needs_update = T.get_from_cache(pokeapi_id)
        if api_object:
            logger.debug("Process %s: got from cache: %s, needs_update: %s", type_name, pokeapi_id, needs_update)
            if needs_update:
                objects_to_update.append(api_object)
        else:
            logger.debug("Process %s: id_: %s not in cache, parsing from csv", type_name, pokeapi_id)
            new_pokeapi_ids.append(pokeapi_id)

    with Session() as session:
        for api_object in objects_to_update:
            api_object = session.merge(api_object)
            object_data = df.loc[api_object.poke_api_id]
            api_object.compare(object_data)
            process_many_to_one(api_object, object_data)
            #df.drop(api_object.poke_api_id, inplace=True)
        session.commit()

    new_objects = T.parse_csv(df.loc[new_pokeapi_ids])
    with Session() as session:
        for new_object in new_objects:
            process_many_to_one(new_object, df.loc[new_object.poke_api_id])
            new_object = session.merge(new_object)
        session.commit()

def process_many_to_one(object: CSVResource, data):
    ins = inspect(object)
    for data_attr_name,object_attr_names  in object.csv_data['relationships'].items(): #object.relationship_attr_map.items():
        logger.debug("process_many_to_one: process: %s for %s", data_attr_name, object_attr_names)
        data_id = data[data_attr_name]
        if data_id is None:
            # assume this is a nullable attribute
            continue
        object_class = getattr(ins.mapper.relationships,object_attr_names.ref).mapper.class_
        object_ref, _ = object_class.get_from_cache(data_id)
        logger.debug("process_many_to_one: object_ref: %s", object_ref)
        setattr(object,object_attr_names.ref,object_ref)
        setattr(object,object_attr_names.key,object_ref.id)

def proces_many_to_many(object, data):
    pass


"""def process_text_entries(api_object):
    # process text entries
    text_entries_relationships = {}
    for rel_name, rel in inspect(api_object).mapper.relationships.items():
        if rel.target.name == 'TextEntry':
            text_entries_relationships[rel_name] = rel

    logger.debug("Process %s: Found %s TextEntry relationships to proecess", type_name, len(text_entries_relationships))
    for text_relationship_name, text_relationship in text_entries_relationships.items():
        text_class = text_relationship.mapper.class_
        text_attr = getattr(api_object, text_relationship_name)
        data_attr = getattr(object_data, text_relationship_name)
        if issubclass(text_class, VersionTextEntry):
            text_entry_map: Dict[str, TextEntry] = { text_entry.text_entry + str(text_entry.language.poke_api_id) + ":" + str(text_entry.version.poke_api_id): text_entry for text_entry in  text_attr}
        elif issubclass(text_class, VersionGroupTextEntry):
            text_entry_map: Dict[str, TextEntry] = { text_entry.text_entry + str(text_entry.language.poke_api_id) + ":" + str(text_entry.version_group.poke_api_id): text_entry for text_entry in  text_attr}
        else:
            text_entry_map: Dict[str, TextEntry] = { text_entry.text_entry + str(text_entry.language.poke_api_id): text_entry for text_entry in  text_attr}
        if len(text_entry_map) > 0:
            logger.debug("Process %s: Found %s existing TextEntries for %s: %s", type_name, len(text_entry_map), type_name, text_relationship_name)
            #logger.debug(text_entry_map) """

    

    

