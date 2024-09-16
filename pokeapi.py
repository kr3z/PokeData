import logging
import pandas as pd
import numpy as np
from math import nan, isnan
from typing import Type, Dict, List
from sqlalchemy import select, inspect, delete

from Base import Session, PokeApiResource, WORKING_DIR, ManyToOneAttrs, CSVResource, FilterOperation, ManyToManyAttr, GroupByCSV
from Berries import Berry, BerryFlavor, BerryFirmness
from Contests import ContestType, ContestEffect, SuperContestEffect
from Evolution import EvolutionChain, EvolutionDetail, EvolutionTrigger
from Encounters import Encounter, EncounterMethod, EncounterCondition, EncounterConditionValue
from Games import Generation, GenerationGameIndex, VersionGroup, Pokedex, VersionGameIndex, Version, PokedexEntry, GameIndex
from Items import Item, ItemAttribute, ItemCategory, ItemFlingEffect, ItemPocket
from Locations import Region, Location, PalParkEncounter, PalParkArea, LocationArea, EncounterMethodRate
from Moves import Move, MoveLearnMethod, Machine, MoveBattleStyle, DamageClass, MoveTarget, MoveCategory, MoveStatChange, PastMoveStatValues, MoveAilment
from Pokemon import Pokemon, PokemonSpecies, EggGroup, PokemonColor, PokemonShape, PokemonHabitat, PokemonStat, PokemonNature, MoveBattleStylePreference, PokeathlonStat, PokemonType, PokemonTypeRelation
from Pokemon import PokemonAbility, PokemonForm, GrowthRate, GrowthRateExperienceLevel, PokemonCharacteristic, PokemonHeldItem, PokemonMove, PokemonAbilityLink
from TextEntries import Language, TextEntry, VersionTextEntry, VersionGroupTextEntry

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
# Version VersionName (version_names.csv has error, introduced in most recent commit, hopefully fixed soon)

### After that we can load any types without links
### Or that only link to Region/Generation/VersionGroup/Version
### Group 1
# BerryFirmness
# ContestType ContestName BerryFlavorName
# ContestEffect ContestEffectEffect ContestEffectFlavorText
# SuperContestEffect SuperContestEffectFlavorText
# EncounterMethod EncounterMethodName
# EncounterCondition EncounterConditionName
# EvolutionTrigger EvolutionTriggerName
# VersionGroup # Depends on Region through many-to-many relationship
## Need to process version_group_regions.csv
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
# MoveFlag MoveFlagName MoveFlagDescription
# EggGroup EggGroupName
# GrowthRate GrowthRateDescription
# PokeathlonStat PokeathlonStatName
# PokemonColor PokemonColorName
# PokemonHabitat PokemonHabitatName
# PokemonShape PokemonShapeName PokemonShapeAwesomName PokemonShapeDescription
# PokemonGender

### Next load types that depend on types in Group 1
### Group 2
# EncounterSlot # VersionGroup EncounterMethod
# EncounterConditionValue EncounterConditionValueName # EncounterCondition
# ItemCategory ItemCategoryName # ItemPocket
# LocationArea LocationAreaName # depends on location
# MoveEffectChange MoveEffectChangeText # Depends on MoveEffect
# Pokedex PokedexName PokedexDescription # Region
# PokemonType PokemonTypeName # Generation/DamageClass
# PokemonStat PokemonStatName # Depends on DamageClass
# GrowthRateExperienceLevel # GrowthRate
# PokemonAbility PokemonAbilityName AbilityFlavorText AbilityEffect # Generation

### Group 3
# Berry # Item BerryFirmness PokemonType
# EncounterMethodRate # depends on LocationArea/EncounterMethod/Version
# Item ItemName ItemFlavorText ItemEffect # ItemFlingEffect ItemCategory
# Move MoveName # Depends on Generation/Type/MoveEffect/MoveTarget/DamageClass/ContestType/ContestEffect/SuperContestEffect
# PokemonAbilityPastEffect AbilityPastEffect # PokemonAbility VersionGroup
# PokemonCharacteristic CharacteristicDescription # PokemonStat
# PokemonTypeRelation # PokemonType/Generation
# PokemonNature/PokemonNatureName # Stat/PokeathlonStat/ContestType

### Group 4
# BerryFlavor # Berry ContestType
# EvolutionChain # Item
# PastMoveStatValues depends on Move/VersionGroup/Type and is not APIResource
# MoveStatChange depends on Move/Stat and is not APIResource
# Machine # Move Item VersionGroup
# MoveBattleStylePreference # PokemonNature/MoveBattleStyle

### Group 5
# PokemonSpecies PokemonName PokemonSpeciesFlavorText PokemonFormDescription PokemonGenus # Generation EvolutionChain PokemonColor PokemonShape PokemonHabitat GrowthRate

### Group 6
# EvolutionDetail # PokemonSpecies EvolutionTrigger Item PokemonGender Location Move PokemonType
# PalParkEncounter
# PokedexEntry # PokemonSpecies Pokedex
# Pokemon # PokemonSpecies

### Group 7
# Encounter # Version LocationArea EncounterSlot Pokemon
# PokemonTypeLink # Pokemon PokemonType
# PokemonPastTypeLink # Pokemon PokemonType Generation
# PokemonAbilityLink # Pokemon PokemonAbility Generation
# PokemonHeldItem # Pokemon Item Version
# PokemonMove # Pokemon Move VersionGroup MoveLearnMethod
# PokemonForm PokemonFormName PokemonFormFormName # Pokemon

### Group 8
# PokemonFormTypeLink # PokemonForm PokemonType
# PokemonFormPokeathlonStat # PokemonForm PokeathlonStat


### Process Game Index Types:
# ItemGameIndex # Item Generation
# TypeGameIndex # depends on Type/Generation
# PokemonGameIndex # Pokemon/Version
# LocationGameIndex # depends on Location/Generation
# FormGameIndex # PokemonForm Generation

## Process Many-to-many relationships
# TODO: Need to implement this processing
# Just keeping a list of csvs for now
# contest_combos.csv
# encounter_condition_value_map.csv
# item_flag_map.csv
# move_flag_map
# pokedex_version_groups.csv
# pokemon_egg_groups.csv
# super_contest_combos.csv
# version_group_pokemon_move_methods.csv
# version_group_regions.csv
    

def process_nonapi_csv(T: Type[CSVResource]):
    type_name = T.__tablename__
    #CSV = CSV_DIR + T.csv_data['primary_csv']
    CSV = CSV_DIR + T.csv_data.primary_csv
    logger.debug("Process non-api CSV file for %s at location: %s", type_name, CSV)
    df = pd.read_csv(CSV,keep_default_na=False,na_values=[''])
    #if T.csv_data.get("concat_csvs"):
    #    for csv_file in T.csv_data.get("concat_csvs"):
    for csv_file in T.csv_data.concat_csvs:
        df2 = pd.read_csv(CSV_DIR + csv_file,keep_default_na=False,na_values=[''])
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
        unique_key = ""
        if issubclass(T, GameIndex):
            unique_key += str(row_data.game_index) + ":"
        elif issubclass(T,PokemonAbilityLink):
            unique_key += str(row_data.slot) + ":"
        elif issubclass(T,PokemonMove):
            unique_key += str(row_data.level) + ":"
        unique_key += ":".join([str(int(row_data[attr_name])) if isinstance(row_data[attr_name],float) else str(row_data[attr_name]) for attr_name in T.csv_data.relationships.keys()])
        for attr_name in T.csv_data.append_unique_attrs:
            unique_key += ":" + str(row_data[attr_name])
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
            #logger.error("Found new idx: %s unique_key: %s", idx, unique_key)
            #raise

    with Session() as session:
        for existing_object, object_data in update_entries_map.items():
            existing_object = session.merge(existing_object, load=False)
            #object_data = df.loc[api_object.poke_api_id]
            existing_object.compare(object_data)
            logger.debug("Process %s: Parsing ManyToOnes for existing object: %s", type_name, existing_object)
            process_relationships(existing_object, object_data, session)
            session.flush()
        session.commit()

    with Session() as session:
        new_objects = []
        for idx,entry_data in df.loc[new_idxs].iterrows():
            new_object: CSVResource = T(entry_data)
            logger.debug("Process %s: Parsing ManyToOnes for new object: %s", type_name, new_object)
            process_relationships(new_object, entry_data, session)
            #new_object = session.merge(new_object)
            new_objects.append(new_object)
        session.add_all(new_objects)
        session.flush()
        """for updated_entry in updated_entries:
            updated_entry = session.merge(updated_entry)
        session.flush() """

        if len(existing_entry_map) > 0:
            logger.debug("Process %s: Found %s existing entries to be deleted for %s", type_name, len(existing_entry_map), type_name)
            for entry_to_delete in existing_entry_map:
                logger.debug("Process %s: Deleting entry: %s", type_name, entry_to_delete)
            #raise
            ids_to_delete: List[int] = [ delete_entry.id for delete_entry in existing_entry_map.values() ]
            session.execute(delete(T).where(T.id.in_(ids_to_delete)))
        session.commit()
            

def process_csv(T: Type[PokeApiResource]):
    type_name = T.__tablename__
    #CSV = CSV_DIR + T.csv_data['primary_csv']
    CSV = CSV_DIR + T.csv_data.primary_csv
    logger.debug("Process CSV file for %s at location: %s", type_name, CSV)
    new_pokeapi_ids = []
    objects_to_update = []
    #df = pd.read_csv(CSV, index_col='id',keep_default_na=False,na_values=[''])
    df = pd.read_csv(CSV,keep_default_na=False,na_values=[''])
    #if T.csv_data.get("merge_csvs"):
    for merge_csv in T.csv_data.merge_csvs:
        #for csv_file, merge_column in T.csv_data.get("merge_csvs").items():
            df2 = pd.read_csv(CSV_DIR + merge_csv.csv,keep_default_na=False,na_values=[''])
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
            #print(df)

            #df.set_index('id', inplace=True)
    if T.csv_data.group_by:
        group_by: GroupByCSV = T.csv_data.group_by
        #df = df.groupby(group_by.grouped_columns).agg({group_by.agg_column: lambda x: list(x)})
        #df = df.groupby(group_by.grouped_columns)[group_by.agg_column].apply(list).reset_index()
        #df = df.groupby(group_by.grouped_columns, as_index=False)[group_by.agg_column].apply(list)
        df = df.groupby(group_by.grouped_columns, as_index=False, dropna=False)[group_by.agg_columns].agg(lambda x: list(x))
        #print(df)
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
            #raise

    with Session() as session:
        for api_object in objects_to_update:
            api_object = session.merge(api_object, load=False)
            object_data = df.loc[api_object.poke_api_id]
            api_object.compare(object_data)
            process_relationships(api_object, object_data, session)
            #df.drop(api_object.poke_api_id, inplace=True)
        session.commit()

    new_objects = T.parse_csv(df.loc[new_pokeapi_ids])
    with Session() as session:
        for new_object in new_objects:
            process_relationships(new_object, df.loc[new_object.poke_api_id], session)
            #new_object = session.merge(new_object)
        session.add_all(new_objects)
        session.commit()

def process_relationships(object: CSVResource, data, session):
    ins = inspect(object)
    for data_attr_name,object_attr_names  in object.csv_data.relationships.items(): #object.relationship_attr_map.items():
        logger.debug("process_relationships: process: %s for %s", data_attr_name, object_attr_names)
        data_id = data[data_attr_name]

        # For many-to-many relationships
        if isinstance(data_id,list):
            #logger.error("data_id: %s",data_id)
            #logger.error("type(data_id): %s", type(data_id))
            #filtered_data_id = [object_id for object_id in data_id if not isnan(object_id)]
            filtered_data_id = []
            for object_id in data_id:
                if not isnan(object_id) and object_id not in filtered_data_id:
                    filtered_data_id.append(object_id)
            
            """ for object_id in data_id:
                if isnan(object_id):
                    #print("deleting nan")
                    data_id.remove(object_id)
                    #break """

            if len(filtered_data_id) == 0:
                continue
            #logger.error("filtered_data_id: %s", filtered_data_id)
            object_class = getattr(ins.mapper.relationships,object_attr_names.ref).mapper.class_
            #print(getattr(ins.mapper.relationships,object_attr_names.ref))
            #logger.error("attr: %s",getattr(object,object_attr_names.ref))
            existing_ids = [object.poke_api_id for object in getattr(object,object_attr_names.ref)]
            new_ids = []
            all_ids = []
            for object_id in filtered_data_id:
                #logger.error("object_id: %s",object_id)
                object_id = int(object_id)
                all_ids.append(object_id)
                if object_id in existing_ids:
                    existing_ids.remove(object_id)
                else:
                    new_ids.append(object_id)
            session.flush()
            if len(existing_ids) > 0 or len(new_ids)>0:
                new_refs = []
                for object_id in all_ids:
                    object_ref, _ = object_class.get_from_cache(object_id)
                    #logger.debug("process_relationships: object_ref: %s", object_ref)
                    new_refs.append(object_ref)
                setattr(object,object_attr_names.ref,new_refs)


        else:
            if data_id is None:
                # assume this is a nullable attribute
                continue
            object_class = getattr(ins.mapper.relationships,object_attr_names.ref).mapper.class_
            object_ref, _ = object_class.get_from_cache(data_id)
            logger.debug("process_relationships: object_ref: %s", object_ref)
            #if isinstance(object_attr_names,ManyToOneAttrs):
            if getattr(object,object_attr_names.key) != object_ref.id:
                setattr(object,object_attr_names.ref,object_ref)
                setattr(object,object_attr_names.key,object_ref.id)
        """ elif isinstance(object_attr_names,ManyToManyAttr):
            object_exists = False
            ref_objects = getattr(object,object_attr_names.ref)
            for ref_object in ref_objects:
                if ref_object.poke_api_id == object_ref.id:
                    object_exists = True
                    break
            if not object_exists:
                ref_objects.append(object_ref)
                setattr(object,object_attr_names.ref,ref_objects) """




    

    

