import time
import logging
from typing import Callable, List, TYPE_CHECKING, Dict, Type

from sqlalchemy import delete, inspect, select
from requests.exceptions import HTTPError
import pokebase
from pokebase.interface import APIResource

from Base import Session, PokeApiResource
from Berries import Berry, BerryFlavor, BerryFlavorLink, BerryFirmness
from Contests import ContestChain, ContestType
from Evolution import EvolutionChain, ChainLink, EvolutionDetail, EvolutionTrigger
from Encounters import Encounter, EncounterMethod, EncounterCondition, EncounterConditionValue
from Games import Generation, GameIndex, GenerationGameIndex, TypeGameIndex, VersionGroup, Pokedex, VersionGameIndex, Version
from Items import Item, ItemAttribute, ItemCategory, ItemFlingEffect, ItemPocket
from Locations import Region, Location, PalParkEncounter, PalParkArea, PokemonEncounter, LocationArea, EncounterMethodRate
from Moves import Move, MoveLearnMethod, Machine, MoveBattleStyle, DamageClass
from Pokemon import Pokemon, PokemonSpecies, EggGroup, PokemonColor, PokemonShape, PokemonHabitat, PokemonStat, PokemonNature, MoveBattleStylePreference, PokeathlonStat, PokemonType, PokemonTypeRelation
from Pokemon import PastTypeLink, PokemonAbility, PokemonForm, GrowthRate, GrowthRateExperienceLevel, PokemonCharacteristic, PokemonHeldItem
from TextEntries import Language, TextEntry, VersionTextEntry, VersionGroupTextEntry

logger = logging.getLogger('PokeBase')
REQ_WAIT_TIME = 1000

class ProcessingInProgressException(Exception):
    pass

POKEBASE_API: Dict[Type[PokeApiResource], Callable] = {
    # Berries
    Berry: pokebase.berry,
    BerryFlavor: pokebase.berry_flavor,
    BerryFirmness: pokebase.berry_firmness,
    # Contests
    ContestType: pokebase.contest_type,
    # Encounters
    EncounterMethod: pokebase.encounter_method,
    EncounterCondition: pokebase.encounter_condition,
    EncounterConditionValue: pokebase.encounter_condition_value,
    # Evolution
    EvolutionChain: pokebase.evolution_chain,
    EvolutionTrigger: pokebase.evolution_trigger,
    # Games
    Generation: pokebase.generation,
    Pokedex: pokebase.pokedex,
    Version: pokebase.version,
    VersionGroup: pokebase.version_group,
    # Items
    Item: pokebase.item,
    ItemAttribute: pokebase.item_attribute,
    ItemCategory: pokebase.item_category,
    ItemFlingEffect: pokebase.item_fling_effect,
    ItemPocket: pokebase.item_pocket,
    # Locations
    Location: pokebase.location,
    LocationArea: pokebase.location_area,
    PalParkArea: pokebase.pal_park_area,
    Region: pokebase.region,
    # Moves
    MoveBattleStyle: pokebase.move_battle_style,
    DamageClass: pokebase.move_damage_class,
    # Pokemon
    PokemonAbility: pokebase.ability,
    PokemonCharacteristic: pokebase.characteristic,
    EggGroup: pokebase.egg_group,
    GrowthRate: pokebase.growth_rate,
    PokemonNature: pokebase.nature,
    PokeathlonStat: pokebase.pokeathlon_stat,
    Pokemon: pokebase.pokemon,
    PokemonForm: pokebase.pokemon_form,
    PokemonSpecies: pokebase.pokemon_species,
    PokemonColor: pokebase.pokemon_color, 
    PokemonShape: pokebase.pokemon_shape,
    PokemonHabitat: pokebase.pokemon_habitat,
    PokemonStat: pokebase.stat,
    PokemonType: pokebase.type_,
    # TextEntries
    Language: pokebase.language
}

def rate_limit(func: Callable):
    def rate_limited_func(self,*args, **kwargs):
        time_since_last_req = round(time.time() * 1000) - self.__class__._last_req
        if time_since_last_req < REQ_WAIT_TIME:
            sleep_time = (REQ_WAIT_TIME - time_since_last_req)/1000.0
            logger.debug("Sleeping for API rate limit: %d ms" ,sleep_time*1000)
            time.sleep(sleep_time)

        ret = None
        try:
            ret = func(self,*args, **kwargs)
        except (HTTPError) as ex:
            logger.error("PokeBase request failed")
            logger.error(ex)
            """ if ex.status_code==404:
                logger.info("404 Error encountered for request. Skipping request and continuing")
            else: """
            raise ex

        self.__class__._last_req = round(time.time() * 1000)

        return ret

    return rate_limited_func

def api_resource(T: Type[PokeApiResource]):
    def api_resource_wrapper(func: Callable):
        def process_api_resource(self, *args, **kwargs):
        #def process_api_resource(self, T: Type[PokeApiResource], id_: int, ignore_404: bool = False) -> PokeApiResource:
            if len(args) > 0:
                id_ = args[0]
            else:
                id_ = kwargs['id_']

            if len(args) > 1:
                ignore_404 = args[1]
            else:
                ignore_404 = kwargs.get('ignore_404')
            if ignore_404 is None:
                ignore_404 = False

            type_name = T.__tablename__
            logger.debug("Process %s: id_: %s", type_name, id_)

            api_object, needs_update = T.get_from_cache(id_)
            if api_object:
                logger.debug("Process %s: got from cache: %s, needs_update: %s", type_name, id_, needs_update)
                """ if api_object not in self._session:
                    #logger.error("TESTING: before get_from_cache merge, current identity_map: %s", self._session.identity_map.items())
                    api_object = self._session.merge(api_object)
                    #logger.error("TESTING: after get_from_cache merge, current identity_map: %s", self._session.identity_map.items()) """
            else:
                logger.debug("Process %s: id_: %s not in cache, retrieving from api", type_name, id_)
            if needs_update:
                object_data = self.get_object_data(T, id_, ignore_404)
                api_url = object_data.url
                if api_url in self._processing:
                    logger.debug("Process %s: id_: %s already being processed", type_name, id_)
                    raise ProcessingInProgressException

                self._processing.add(api_url)
                #self._session.flush()

                try:
                    if api_object:
                        logger.debug("Process %s: Comparing existing object to API data for id: %s", type_name, id_)
                        api_object.compare(object_data)
                    else:
                        logger.debug("Process %s: id_: %s not in cache, retrieving from api", type_name, id_)
                        api_object = T.parse_data(object_data)

                    #logger.error("TESTING: before func, current identity_map: %s", self._session.identity_map.items())
                    api_object = func(api_object, object_data, self,*args, **kwargs)

                    #logger.error("TESTING: after func, current identity_map: %s", self._session.identity_map.items())

                    """ try:
                        #api_object = self._session.merge(api_object)
                        if api_object not in self._session:
                            logger.debug("Process %s: Merging api_object with id_: %s", type_name, id_)
                            api_object = self._session.merge(api_object)
                            #self._session.add(api_object)
                            self._session.flush()
                    except Exception as ex:
                        logger.error("ERROR: adding object of type: %s", type_name)
                        logger.error("api_object: %s", api_object)
                        logger.error("object_data: %s", object_data)
                        raise ex  """
                    
                    with Session() as session:
                        logger.debug("Process %s: Merging api_object with id_: %s", type_name, id_)
                        api_object = session.merge(api_object)
                        #session.commit()


                        # process game_indices
                        if hasattr(T, 'game_indices'):
                            gi_class = T.game_indices.property.mapper.class_
                            if issubclass(gi_class, GenerationGameIndex):
                                gi_entry_map: Dict[str, GenerationGameIndex] = {str(api_object.poke_api_id) + ":" + str(gi.generation.poke_api_id) + ":" + str(gi.game_index): gi for gi in api_object.game_indices}
                            else:
                                gi_entry_map: Dict[str, VersionGameIndex] = {str(api_object.poke_api_id) + ":" + str(gi.version.poke_api_id) + ":" + str(gi.game_index): gi for gi in api_object.game_indices}
                            if len(gi_entry_map) > 0:
                                logger.debug("Process GameIndex: Found %s existing GameIndex entries for object type: %s and id_: %s", len(gi_entry_map), type_name, object_data.id_)
            
                            for gi_data in object_data.game_indices:
                                game_index = gi_data.game_index
                                if issubclass(gi_class, GenerationGameIndex):
                                    #generation_id = gi_data.generation.id_
                                    #generation = self.process_generation(generation_id)
                                    gi_type_id = gi_data.generation.id_
                                    gi_type_object = self.process_generation(gi_type_id)
                                else: # VersionGameIndex
                                    #version_id = gi_data.version.id_
                                    #version = self.process_version(version_id)
                                    gi_type_id = gi_data.version.id_
                                    gi_type_object = self.process_version(gi_type_id)

                                map_key = str(object_data.id_) + ":" + str(gi_type_id) + ":" + str(game_index) #object_id:generation_id:game_index
                                gi = gi_entry_map.pop(map_key, None)

                                if not gi:
                                    logger.debug("Process GameIndex: Parsing new GameIndex for type: %s gi_type_id: %s game_index; %s", type_name, gi_type_id, game_index)
                                    gi_object = gi_class(game_index)
                                    if isinstance(gi_object, GenerationGameIndex):
                                        gi_object.generation = gi_type_object
                                        gi_object.generation_key = gi_type_object.id
                                    else: # VersionGameIndex
                                        gi_object.version = gi_type_object
                                        gi_object.version_key = gi_type_object.id
                                    gi_object.object_key = api_object.id
                                    gi_object.object_ref = api_object
                                    
                                    gi_object = session.merge(gi_object)
                                    session.flush()

                            if gi_entry_map:
                                logger.debug("Process GameIndex: Found %s existing GameIndex entries to be deleted for type: %s", len(gi_entry_map), type_name)
                                gi_ids_to_delete: List[int] = [ gi.id for gi in gi_entry_map.values() ]
                                with Session() as session:
                                    session.execute(delete(gi_class).where(gi_class.id.in_(gi_ids_to_delete)))
                                    session.commit()
                                #self._session.execute(delete(gi_class).where(gi_class.id.in_(gi_ids_to_delete)))

                        # process text entries
                        text_entries_relationships = {}
                        for rel_name, rel in inspect(api_object).mapper.relationships.items():
                            if rel.target.name == 'TextEntry':
                                text_entries_relationships[rel_name] = rel

                        logger.debug("Process %s: Found %s TextEntry relationships to proecess", type_name, len(text_entries_relationships))
                        #with Session() as session:
                        #api_object = session.merge(api_object)
                        for text_relationship_name, text_relationship in text_entries_relationships.items():
                            #logger.debug("processing text_relationship_name: %s", text_relationship_name)
                            text_class = text_relationship.mapper.class_
                            text_attr = getattr(api_object, text_relationship_name)
                            #logger.debug("text_attr: %s", text_attr)
                            data_attr = getattr(object_data, text_relationship_name)
                            if issubclass(text_class, VersionTextEntry):
                                text_entry_map: Dict[str, TextEntry] = { text_entry.text_entry + str(text_entry.language.poke_api_id) + ":" + str(text_entry.version.poke_api_id): text_entry for text_entry in  text_attr}
                            elif issubclass(text_class, VersionGroupTextEntry):
                                text_entry_map: Dict[str, TextEntry] = { text_entry.text_entry + str(text_entry.language.poke_api_id) + ":" + str(text_entry.version_group.poke_api_id): text_entry for text_entry in  text_attr}
                            else:
                                text_entry_map: Dict[str, TextEntry] = { text_entry.text_entry + str(text_entry.language.poke_api_id): text_entry for text_entry in  text_attr}
                            if len(text_entry_map) > 0:
                                logger.debug("Process %s: Found %s existing TextEntries for %s: %s", type_name, len(text_entry_map), type_name, text_relationship_name)
                                #logger.debug(text_entry_map)

                            for text_data in data_attr:
                                text_key = getattr(text_data, text_class.text_entry_name) + str(text_data.language.id_)
                                version_id_ = None
                                if issubclass(text_class, VersionTextEntry):
                                    version_id_ = text_data.version.id_
                                if issubclass(text_class, VersionGroupTextEntry):
                                    version_id_ = text_data.version_group.id_
                                if version_id_:
                                    text_key = text_key + ":" + str(version_id_)
                                #logger.debug("Process %s: Checking for existing text_key: %s", type_name, text_key)
                                text_entry = text_entry_map.pop(text_key, None)
                                #logger.debug("text_entry: %s", text_entry)

                                if not text_entry:
                                    logger.debug("Process %s: Parsing new TextEntry: %s", type_name, text_key)
                                    
                                    object_text: TextEntry = text_class(text_data)
                                    object_text.object_key = api_object.id
                                    object_text.object_ref = api_object

                                    """ if api_object.id is None:
                                        logger.error("ERROR: api_object has null id? api_object: %s", api_object)
                                        raise

                                    if object_text.object_key is None:
                                        logger.error("ERROR: object_text has null object_key? object_text: %s", object_text)
                                        raise """

                                    #Recursively process language
                                    #logger.error("TESTING: Pre-process_language: object_text.id: %s object_key: %s object_ref: %s text_data.language.id_: %s", object_text.id, object_text.object_key, object_text.object_ref, text_data.language.id_)
                                    #logger.error("TESTING: Pre-process_language, current identity_map: %s", self._session.identity_map.items())
                                    object_text_language = self.process_language(text_data.language.id_, ignore_404=False)
                                    #object_text_language = self._session.merge(object_text_language)
                                    object_text.language = object_text_language
                                    object_text.language_key = object_text_language.id

                                    if isinstance(object_text, VersionTextEntry):
                                        version = self.process_version(text_data.version.id_)
                                        object_text.version_key = version.id
                                        object_text.version = version

                                    elif isinstance(object_text, VersionGroupTextEntry):
                                        vg = self.process_version_group(text_data.version_group.id_)
                                        object_text.version_group_key = vg.id
                                        object_text.version_group = vg

                                    #logger.error("TESTING: object_text.id: %s object_key: %s language_key: %s api_object.id: %s api_object type: %s", object_text.id, object_text.object_key, object_text.language_key, api_object.id, type_name)

                                    #logger.error("TESTING: Calling session.add, current identity_map: %s", self._session.identity_map.items())
                                    #self._session.add(object_text)
                                    """ with Session() as session:
                                        session.add(object_text)
                                        session.commit() """
                                    #logger.error("TESTING: Calling session.flush, current identity_map: %s", self._session.identity_map.items())
                                    #self._session.flush()

                                    #logger.error("TESTING: adding links")

                                    #logger.error("TESTING before append text_attr: object_text.id: %s object_key: %s language_key: %s api_object.id: %s api_object type: %s", object_text.id, object_text.object_key, object_text.language_key, api_object.id, type_name)

                                    #text_attr.append(object_text)
                                    #logger.error("TESTING after append text_attr: object_text.id: %s object_key: %s language_key: %s api_object.id: %s api_object type: %s", object_text.id, object_text.object_key, object_text.language_key, api_object.id, type_name)
                                    #object_text_language.names.append(object_text)
                                    #logger.error("TESTING after append language: object_text.id: %s object_key: %s language_key: %s api_object.id: %s api_object type: %s", object_text.id, object_text.object_key, object_text.language_key, api_object.id, type_name)
                                    object_text = session.merge(object_text)
                                    session.flush()





                            remaining_text_entries = len(text_entry_map)
                            if remaining_text_entries > 0:
                                logger.debug("Process %s: Found %s existing TextEntries to be deleted for %s: %s", remaining_text_entries, type_name, api_object.id)
                                for text_to_delete in text_entry_map:
                                    logger.debug("Process %s: Deleting TextEntry: %s", type_name, text_to_delete)
                                text_ids_to_delete: List[int] = [ text_entry.id for text_entry in text_entry_map.values() ]
                                #with Session() as session:
                                session.execute(delete(text_class).where(text_class.id.in_(text_ids_to_delete)))
                                #session.commit()
                                #self._session.execute(delete(text_class).where(text_class.id.in_(text_ids_to_delete)))
                        session.commit()


                    #if hasattr(T, 'names'):
                    #    self.process_names(api_object, object_data)

                    #if hasattr(T, 'awesome_names'):

                    """ try:
                        #api_object = self._session.merge(api_object)
                        if api_object not in self._session:
                            logger.debug("Process %s: Merging api_object with id_: %s", type_name, id_)
                            #logger.debug("Process %s: adding api_object with id_: %s", type_name, id_)
                            api_object = self._session.merge(api_object)
                            if isinstance(api_object, PokeApiResource):
                                api_object.recache() 
                            #self._session.add(api_object)
                    except Exception as ex:
                        logger.error("ERROR: adding object of type: %s", type_name)
                        logger.error("api_object: %s", api_object)
                        logger.error("object_data: %s", object_data)
                        raise ex  """
                    #self._session.commit()

                finally:
                    self._processing.remove(api_url)

            return api_object

        return process_api_resource
    return api_resource_wrapper

class PokeBaseWrapper:
    _last_req: int = 0

    def __init__(self):
        #self._session = Session()
        self._processing = set()

        # Make sure stats are loaded before anything else
        #for stat_id in range(1,7):
        #    self.process_stat(stat_id, skip_nature = True)

    """ def close(self):
        self._session.close() """

    @rate_limit
    def get_object_data(self, T: Type[PokeApiResource], id_: int, ignore_404: bool = False) -> APIResource:
        object_data = None
        try: 
            object_data = POKEBASE_API[T](id_)
        except HTTPError as ex:
            if ex.response.status_code == 404 and ignore_404:
                logger.info("404 Error encountered for request. Skipping request and continuing")
            else: 
                raise ex
        return object_data

    """ @rate_limit
    def get_species_data(self,species_id: int) -> APIResource:
        species_data = None
        try: 
            species_data = pokebase.pokemon_species(species_id)
        except HTTPError as ex:
            if ex.response.status_code != 404:
                raise ex
            #else:
            #    return None
        return species_data """
# Berries

    @api_resource(Berry)
    def process_berry(berry: Berry, berry_data: APIResource, self, id_: int, ignore_404: bool = False) -> Berry:

        firmness_data = berry_data.firmness
        firmness = self.process_berry_firmness(firmness_data.id_)
        berry.firmness_key = firmness.id
        berry.firmness = firmness

        item_data = berry_data.item
        item = self.process_item(item_data.id_)
        berry.item_key = item.id
        berry.item = item
        
        type_data = berry_data.natural_gift_type
        type_ = self.process_type(type_data.id_)
        berry.natural_gift_type_key = type_.id
        berry.natural_gift_type = type_

        return berry
    
    
    def process_berry_flavor_link(self, link_data, flavor: BerryFlavor) -> BerryFlavorLink:
        berry_id = link_data.berry.id_

        processing_key = "BerryFlavorLink:"+str(berry_id)+":"+str(flavor.poke_api_id)
        if processing_key in self._processing:
            logger.debug("process_berry_flavor_link: berry flavor link for Berry: %s and BerryFlavor: %s already being processed", berry_id, flavor.poke_api_id)
            raise ProcessingInProgressException
        
        self._processing.add(processing_key)
        try:
            berry = self.process_berry(berry_id)
            stmt = select(BerryFlavorLink).filter_by(berry_key=berry.id, flavor_key=flavor.id)
            with Session() as session:
                link: BerryFlavorLink = session.scalars(stmt).first()
            if link:
                link.compare(link_data)
            else:
                link = BerryFlavorLink.parse_data(link_data)
            
            link.berry = berry
            link.berry_key = berry.id
            link.flavor = flavor
            link.flavor_key = flavor.id

            with Session() as session:
                link = session.merge(link)
                session.commit()

        finally:
            self._processing.remove(processing_key)

        return link
    
    @api_resource(BerryFirmness)
    def process_berry_firmness(firmness: BerryFirmness, firmness_data: APIResource, self, id_: int, ignore_404: bool = False) -> BerryFirmness:

        return firmness

    @api_resource(BerryFlavor)
    def process_berry_flavor(flavor: BerryFlavor, flavor_data: APIResource, self, id_: int, ignore_404: bool = False) -> BerryFlavor:

        contest_type_data = flavor_data.contest_type
        contest_type: ContestType = self.process_contest_type(contest_type_data.id_)
        flavor.contest_type = contest_type
        flavor.contest_type_key = contest_type.id
        # Shouldn't need to do this, populating contest_type/key is all we need
        ## one-to-one mapping, so populate relationship for otherside
        #contest_type.berry_flavor = flavor
        #contest_type.berry_flavor_key = flavor.id

        for link_data in flavor_data.berries:
            link = self.process_berry_flavor_link(link_data=link_data, flavor=flavor)

        return flavor
    
# Contests
    @api_resource(ContestType)
    def process_contest_type(contest_type: ContestType, type_data: APIResource, self, id_: int, ignore_404: bool = False) -> ContestType:

        #Shouldn't need to do this since the reference is on the berry flavor side
        """ berry_flavor_data = type_data.berry_flavor
        berry_flavor: BerryFlavor = self.process_berry_flavor(berry_flavor_data.id_)
        #if not contest_type.berry_flavor:
        contest_type.berry_flavor = berry_flavor
        contest_type.berry_flavor_key = berry_flavor.id
        # one-to-one mapping, so populate relationship for otherside
        #if not berry_flavor.contest_type:
        berry_flavor.contest_type = contest_type
        berry_flavor.contest_type_key = contest_type.id """

        return contest_type
    
#Encounters

    def process_encounter(self, encounter_data, pokemon_encounter: PokemonEncounter) -> Encounter:
        method_id = encounter_data.method.id_
        processing_key = "Encounter:"+str(pokemon_encounter.id) + ":" + str(method_id)
        if processing_key in self._processing:
            logger.debug("process_encounter: encounter for PokemonEncouter: %s and method: %s already being processed", pokemon_encounter.id, method_id)
            raise ProcessingInProgressException
        
        self._processing.add(processing_key)
        try:
            method = self.process_encounter_method(method_id)
            with Session() as session:
                encounter = session.scalars(select(Encounter).filter_by(pokemon_encounter_key=pokemon_encounter.id, method_key = method.id)).first()
            if encounter:
                encounter.compare(encounter_data)
            else:
                encounter = Encounter.parse_data(encounter_data)

            if encounter.pokemon_encounter_key != pokemon_encounter.id:
                encounter.pokemon_encounter_key = pokemon_encounter.id
                encounter.pokemon_encounter = pokemon_encounter
            if encounter.method_key != method.id:
                encounter.method_key = method.id
                encounter.method = method

            with Session() as session:
                encounter = session.merge(encounter)
                existing_value_ids = {value.poke_api_id for value in encounter.condition_values}
                for value_data in encounter_data.condition_values:
                    if value_data.id_ not in existing_value_ids:
                        value = self.process_encounter_condition_value(value_data.id_)
                        value = session.merge(value)
                        encounter.condition_values.append(value)
                session.commit()

            """ with Session() as session:
                encounter = session.merge(encounter)
                session.commit() """
        finally:
            self._processing.remove(processing_key)

        return encounter


    @api_resource(EncounterMethod)
    def process_encounter_method(method: EncounterMethod, method_data: APIResource, self, id_: int, ignore_404: bool = False) -> EncounterMethod:
        
        return method
    
    @api_resource(EncounterCondition)
    def process_encounter_condition(condition: EncounterCondition, condition_data: APIResource, self, id_: int, ignore_404: bool = False) -> EncounterCondition:
        
        return condition
    
    @api_resource(EncounterConditionValue)
    def process_encounter_condition_value(value: EncounterConditionValue, value_data: APIResource, self, id_: int, ignore_404: bool = False) -> EncounterConditionValue:
        condition_data = value_data.condition
        condition = self.process_encounter_condition(condition_data.id_)
        value.condition_key = condition.id
        value.condition = condition

        return value

# Evolution

    @api_resource(EvolutionChain)
    def process_evolution_chain(evolution_chain: EvolutionChain, evolution_chain_data: APIResource, self, id_: int, ignore_404: bool = False) -> EvolutionChain:

        #baby_trigger_item
        if evolution_chain_data.baby_trigger_item:
            baby_trigger_item_id = evolution_chain_data.baby_trigger_item.id_
            baby_trigger_item = self.process_item(baby_trigger_item_id)
            evolution_chain.baby_trigger_item = baby_trigger_item
            evolution_chain.baby_trigger_item_key = baby_trigger_item.id

        #chain
        chain_data = evolution_chain_data.chain
        chain = self.process_chain_link(chain_data = chain_data)
        evolution_chain.chain = chain
        evolution_chain.chain_key = chain.id

        return evolution_chain
    
    def process_chain_link(self, chain_data, evolves_from: ChainLink = None) -> ChainLink:
        link_species_id = chain_data.species.id_
        link_species: PokemonSpecies = self.process_pokemon_species(link_species_id)

        processing_key = "ChainLink:"+str(link_species_id)
        if processing_key in self._processing:
            logger.debug("process_chain_link: chain link for species_id: %s already being processed", link_species_id)
            raise ProcessingInProgressException
        
        self._processing.add(processing_key)
        try:
            with Session() as session:
                chain = session.scalars(select(ChainLink).filter_by(species_key=link_species.id)).first()
            if chain:
                chain.compare(chain_data)
            else:
                chain = ChainLink.parse_data(chain_data)

            chain.species = link_species
            chain.species_key = link_species.id
            if evolves_from:
                chain.evolves_from = evolves_from
                chain.evolves_from_key = evolves_from.id

            #evolves_to
            for evolves_to_data in chain_data.evolves_to:
                evolves_to = self.process_chain_link(evolves_to_data, chain)

            #evolution_details
            for chain_idx, evolution_details_data in enumerate(chain_data.evolution_details):
                variety_idx = 0
                pokemon = None
                for variety in chain_data.species.varieties:
                    if not variety.pokemon.forms[0].is_mega:
                        if chain_idx == variety_idx:
                            pokemon = self.process_pokemon(variety.pokemon.id_)
                            break
                        variety_idx += 1
                if not pokemon:
                    logger.error("Didn't find a pokemon for evolution_details. Species: %s chain_idx: %s", link_species.name, chain_idx)
                    raise Exception("No pokemon for evolution_details")
                evolution_details = self.process_evolution_details(evolution_details_data, chain, pokemon)

            with Session() as session:
                chain = session.merge(chain)
                session.commit()
        finally:
            self._processing.remove(processing_key)
        
        return chain

    def process_evolution_details(self, details_data, chain: ChainLink, pokemon: Pokemon) -> EvolutionDetail:
        #processing_key = "EvolutionDetails:"+str(chain.id)+":"+str(details_data.trigger.id_)
        processing_key = "EvolutionDetails:"+str(pokemon.poke_api_id)
        if processing_key in self._processing:
            logger.debug("process_evolution_details: evolution details for chain.id: %s and trigger.poke_api_id: %s already being processed", chain.id, details_data.trigger.id_)
            raise ProcessingInProgressException
        
        self._processing.add(processing_key)
        try:
            with Session() as session:
                details = session.scalars(select(EvolutionDetail).filter_by(pokemon_key=pokemon.id)).first()
            if details:
                details.compare(details_data)
            else:
                details = EvolutionDetail.parse_data(details_data)


            details.chain_link = chain
            details.chain_link_key = chain.id

            #pokemon # How?!
            # need to process species.varieties before evolution chain
            # That will give unique attribute to query on above
            # The pokemon in varieties should (hopefully!) be in the same order as evolution details
            # but varieties will also contain megas
            # slowbros varieties are [slowbro, mega, galar]
            # slowbros evo details are [slowbro, galar]
            # so need to filter megas from varieties and then apply to evo details
            #pokemon_key: Mapped[int] = mapped_column(Integer)

            details.pokemon = pokemon
            details.pokemon_key = pokemon.id

            trigger = self.process_evolution_trigger(details_data.trigger.id_)
            details.trigger = trigger
            details.trigger_key = trigger.id

            if details_data.item:
                item = self.process_item(details_data.item.id_)
                details.item = item
                details.item_key = item.id

            if details_data.held_item:
                held_item = self.process_item(details_data.held_item.id_)
                details.held_item = held_item
                details.held_item_key = held_item.id

            if details_data.known_move:
                known_move = self.process_move(details_data.known_move.id_)
                details.known_move = known_move
                details.known_move_key = known_move.id

            if details_data.known_move_type:
                known_move_type = self.process_pokemon_type(details_data.known_move_type.id_)
                details.known_move_type = known_move_type
                details.known_move_type_key = known_move_type.id

            if details_data.location:
                location = self.process_location(details_data.location.id_)
                details.location = location
                details.location_key = location.id

            if details_data.party_species:
                party_species = self.process_pokemon_species(details_data.party_species.id_)
                details.party_species = party_species
                details.party_species_key = party_species.id

            if details_data.party_type:
                party_type = self.process_pokemon_type(details_data.party_type.id_)
                details.party_type = party_type
                details.party_type_key = party_type.id

            if details_data.trade_species:
                trade_species = self.process_pokemon_species(details_data.trade_species.id_)
                details.trade_species = trade_species
                details.trade_species_key = trade_species.id

            with Session() as session:
                details = session.merge(details)
                session.commit()

        finally:
            self._processing.remove(processing_key)

        return details

    
    @api_resource(EvolutionTrigger)
    def process_evolution_trigger(trigger: EvolutionTrigger, trigger_data: APIResource, self, id_: int, ignore_404: bool = False) -> EvolutionTrigger:
        return trigger
    
# Games
    @api_resource(Generation)
    def process_generation(generation: Generation, generation_data: APIResource, self, id_: int, ignore_404: bool = False) -> Generation:
        #logger.error("TESTING: in process_generation for id_: %s, current identity_map: %s", id_, self._session.identity_map.items())
        region_data = generation_data.main_region
        region: Region = self.process_region(region_data.id_)
        #generation.region_key = region.id
        generation.main_region = region
        if not region.generation_key:
            region.generation_key = generation.id

        #logger.error("TESTING: in process_generation after region for id_: %s, current identity_map: %s", id_, self._session.identity_map.items())

        """ if generation not in self._session:
            generation = self._session.merge(generation) """
        #logger.error("TESTING: in process_generation after merge for id_: %s, current identity_map: %s", id_, self._session.identity_map.items())
        with Session() as session:
            generation = session.merge(generation)
            existing_vg_ids = {vg.poke_api_id for vg in generation.version_groups}
            for vg_data in generation_data.version_groups:
                if vg_data.id_ not in existing_vg_ids:
                    vg = self.process_version_group(vg_data.id_)
                    #if vg not in generation.version_groups:
                    generation.version_groups.append(vg)
            session.commit()
        
            
        return generation
    

    @api_resource(Pokedex)
    def process_pokedex(pokedex: Pokedex, pokedex_data: APIResource, self, id_: int, ignore_404: bool = False) -> Pokedex:
        region_data = pokedex_data.region
        region = self.process_region(region_data.id_)
        pokedex.region_key = region.id
        pokedex.region = region

        #if pokedex not in self._session:
        #if inspect(pokedex).detached:
        #    self._session.add(pokedex) # need to add pokedex to a session before we can acess the version_groups attribute
        """ if pokedex not in self._session:
            pokedex = self._session.merge(pokedex) """
        with Session() as session:
            pokedex = session.merge(pokedex)
            existing_vg_ids = {vg.poke_api_id for vg in pokedex.version_groups}
            for vg_data in pokedex_data.version_groups:
                if vg_data.id_ not in existing_vg_ids:
                    vg = self.process_version_group(vg_data.id_)
                    vg = session.merge(vg)
                    #if vg not in pokedex.version_groups:
                    pokedex.version_groups.append(vg)
            session.commit()

        # Do we also want to load each dex entry?
        # Maybe not right now

        return pokedex


    @api_resource(Version)
    def process_version(version: Version, version_data: APIResource, self, id_: int, ignore_404: bool = False) -> Version:
        vg_data = version_data.version_group
        vg = self.process_version_group(vg_data.id_)
        version.version_group_key = vg.id
        version.version_group = vg

        return version

    @api_resource(VersionGroup)
    def process_version_group(version_group: VersionGroup, version_group_data: APIResource, self, id_: int, ignore_404: bool = False) -> VersionGroup:
        #logger.error("TESTING: in process_version_group for id_: %s, current identity_map: %s", id_, self._session.identity_map.items())
        generation = self.process_generation(version_group_data.generation.id_)
        version_group.generation = generation
        version_group.generation_key = generation.id

        #logger.error("TESTING: in process_version_group after generation for id_: %s, current identity_map: %s", id_, self._session.identity_map.items())

        #if version_group not in self._session:
        #if inspect(version_group).detached:
        #    self._session.add(version_group) # need to add version_group to a session before we can acess the regions/pokedexes attributes
        """ if version_group not in self._session:
            version_group = self._session.merge(version_group) """
        #logger.error("TESTING: in process_version_group after merge for id_: %s, current identity_map: %s", id_, self._session.identity_map.items())
        with Session() as session:
            version_group = session.merge(version_group)
            existing_region_ids = {region.poke_api_id for region in version_group.regions}
            for region_data in version_group_data.regions:
                if region_data.id_ not in existing_region_ids:
                    region = self.process_region(region_data.id_)
                    region = session.merge(region)
                    #logger.error("TESTING: in process_version_group after process_region for id_: %s, current identity_map: %s", id_, self._session.identity_map.items())
                    #if region not in version_group.regions:
                    version_group.regions.append(region)
            session.commit()

        """ with Session() as session:
            version_group = session.merge(version_group)
            existing_pokedex_ids = {pokedex.poke_api_id for pokedex in version_group.pokedexes}
            for pokedex_data in version_group_data.pokedexes:
                if pokedex_data.id_ not in existing_pokedex_ids:
                    pokedex = self.process_pokedex(pokedex_data.id_)
                    pokedex = session.merge(pokedex)
                    #if pokedex not in self._session:
                    #    pokedex = self._session.merge(pokedex)
                    #if pokedex not in version_group.pokedexes:
                    version_group.pokedexes.append(pokedex)
            session.commit() """

        return version_group
    
# Items
    @api_resource(Item)
    def process_item(item: Item, item_data: APIResource, self, id_: int, ignore_404: bool = False) -> Item:

        fling_effect_data = item_data.fling_effect
        if fling_effect_data:
            fling_effect = self.process_fling_effect(fling_effect_data.id_)
            item.fling_effect = fling_effect
            item.fling_effect_key = fling_effect.id

        
        category_data = item_data.category
        category = self.process_item_category(category_data.id_)
        item.category = category
        item.category_key = category.id

        # This should be done from the berry side, through berry flavor
        #berry: Mapped["Berry"] = relationship(#back_populates="item",
        #                                      primaryjoin="Item.berry_key == Berry.id",
        #                                      foreign_keys=berry_key, cascade="save-update")

        with Session() as session:
            item = session.merge(item)
            existing_attribute_ids = {attribute.poke_api_id for attribute in item.attributes}
            for attribute_data in item_data.attributes:
                if attribute_data.id_ not in existing_attribute_ids:
                    attribute = self.process_item_attribute(attribute_data.id_)
                    attribute = session.merge(attribute)
                    item.attributes.append(attribute)
            session.commit()

        # should be handled in decorator
        #game_indices: Mapped[List["ItemGameIndex"]] = relationship(back_populates="object_ref", cascade="save-update",
        #                                                           primaryjoin="Item.id == foreign(ItemGameIndex.object_key)")
        
        # Populate from the Machine side, through Move
        #machines: Mapped[List["Machine"]] = relationship(back_populates="item", cascade="save-update",
        #                                                 primaryjoin="Item.id == foreign(Machine.item_key)")
    
    
        return item
    
    @api_resource(ItemAttribute)
    def process_item_attribute(attribute: ItemAttribute, attribute_data: APIResource, self, id_: int, ignore_404: bool = False) -> ItemAttribute:
        return attribute
    
    @api_resource(ItemCategory)
    def process_item_category(category: ItemCategory, category_data: APIResource, self, id_: int, ignore_404: bool = False) -> ItemCategory:
        pocket_data = category_data.pocket
        pocket = self.process_item_pocket(pocket_data.id_)
        category.pocket_key = pocket.id
        category.pocket = pocket

        return category
    
    @api_resource(ItemFlingEffect)
    def process_fling_effect(fling: ItemFlingEffect, fling_data: APIResource, self, id_: int, ignore_404: bool = False) -> ItemFlingEffect:
        return fling
    
    @api_resource(ItemPocket)
    def process_item_pocket(pocket: ItemPocket, pocket_data: APIResource, self, id_: int, ignore_404: bool = False) -> ItemPocket:
        return pocket

# Locations
    @api_resource(Location)
    def process_location(location: Location, location_data: APIResource, self, id_: int, ignore_404: bool = False) -> Location:
        region_data = location_data.region
        region = self.process_region(region_data.id_)
        location.region_key = region.id
        location.region = region

        return location
    
    @api_resource(LocationArea)
    def process_location_area(area: LocationArea, area_data: APIResource, self, id_: int, ignore_404: bool = False) -> LocationArea:
        location_data = area_data.location
        location = self.process_location(location_data.id_)
        area.location_key = location.id
        area.location = location

        for rate_data in area_data.encounter_method_rates:
            method_id = rate_data.encounter_method.id_
            for version_detail in rate_data.version_details:
                rate = self.process_encounter_method_rate(version_detail, method_id, area)

        return area
    
    def process_encounter_method_rate(self, version_details, method_id: int, area: LocationArea):
        version_id = version_details.version.id_
        processing_key = "EncounterMethodRate:"+str(area.poke_api_id) + ":" + str(version_id) + ":" + str(method_id)
        if processing_key in self._processing:
            logger.debug("process_encounter_method_rate: EncounterMethodRate for area: %s and version: %s and method: %s already being processed", area.poke_api_id, version_id, method_id)
            raise ProcessingInProgressException
        
        self._processing.add(processing_key)
        try:
            method = self.process_encounter_method(method_id)
            version = self.process_version(version_id)
            with Session() as session:
                rate = session.scalars(select(EncounterMethodRate).filter_by(location_area_key=area.id, version_key=version.id, encounter_method_key=method.id)).first()
            if rate:
                rate.compare(version_details)
            else:
                rate = EncounterMethodRate.parse_data(version_details)

            rate.encounter_method_key = method.id
            rate.encounter_method = method
            rate.version_key = version.id
            rate.version = version
            rate.location_area_key = area.id
            rate.location_area = area
            
            with Session() as session:
                rate = session.merge(rate)
                session.commit()

        finally:
            self._processing.remove(processing_key)

        return rate

    def process_pokemon_encounter(self, version_details, area_id: int, pokemon: Pokemon) -> PokemonEncounter:
        version_id = version_details.version.id_
        processing_key = "PokemonEncounter:"+str(pokemon.poke_api_id) + ":" + str(version_id) + ":" + str(area_id)
        if processing_key in self._processing:
            logger.debug("process_pokemon_encounter: PokemonEncounter for pokemon: %s and version: %s and area: %s already being processed", pokemon.poke_api_id, version_id, area_id)
            raise ProcessingInProgressException
        
        self._processing.add(processing_key)
        try:
            area = self.process_location_area(area_id)
            version = self.process_version(version_id)
            with Session() as session:
                encounter = session.scalars(select(PokemonEncounter).filter_by(pokemon_key=pokemon.id, version_key=version.id, location_area_key=area.id)).first()
            if encounter:
                encounter.compare(version_details)
            else:
                encounter = PokemonEncounter.parse_data(version_details)

            encounter.pokemon_key = pokemon.id
            encounter.pokemon = pokemon
            encounter.version_key = version.id
            encounter.version = version
            encounter.location_area_key = area.id
            encounter.location_area = area

            for details in version_details.encounter_details:
                self.process_encounter(details, encounter)
            
            with Session() as session:
                encounter = session.merge(encounter)
                session.commit()

        finally:
            self._processing.remove(processing_key)

        return encounter
    
    @api_resource(PalParkArea)
    def process_pal_park_area(area: PalParkArea, area_data: APIResource, self, id_: int, ignore_404: bool = False) -> PalParkArea:
        return area

    def process_pal_park_encounter(self, pal_park_data, species: PokemonSpecies) -> PokemonSpecies:
        base_score = pal_park_data.base_score
        rate = pal_park_data.rate
        area_data = pal_park_data.area

        """ for encounter_data in area_data.pokemon_encounters:
            if encounter_data.pokemon_species.id_ == species.poke_api_id:
                break

        if encounter_data.pokemon_species.id_ != species.poke_api_id:
            logger.error("process_pal_park_encounter: Species: %s not found in PalParkArea: %s", species.poke_api_id, area_data.id_)
            raise Exception("Error processing Pal Park data")
        
        rarity = encounter_data.rarity """
        
        processing_key = "PalParkEncounter:"+str(species.poke_api_id) + ":" + str(area_data.id_)
        if processing_key in self._processing:
            logger.debug("process_pal_park_encounter: Pal Park Encounter for Species: %s and PalParkArea: %s already being processed", species.poke_api_id, area_data.id_)
            raise ProcessingInProgressException
        
        self._processing.add(processing_key)
        try:
            area = self.process_pal_park_area(area_data.id)
            with Session() as session:
                encounter = session.scalars(select(PalParkEncounter).filter_by(pokemon_species_key=species.id, pal_park_area_key=area.id)).first()
            if encounter:
                encounter.compare(base_score=base_score, rate=rate)
            else:
                encounter = PalParkEncounter.parse_data(base_score=base_score, rate=rate)

            encounter.pokemon_species = species
            encounter.pokemon_species_key = species.id
            encounter.pal_park_area = area
            encounter.pal_park_area_key = area.id
            
            with Session() as session:
                encounter = session.merge(encounter)
                session.commit()

        finally:
            self._processing.remove(processing_key)

        return encounter
    
    @api_resource(Region)
    def process_region(region: Region, region_data: APIResource, self, id_: int, ignore_404: bool = False) -> Region:
        generation_data = region_data.main_generation
        # Hisui doesn't have a generation
        if generation_data:
            generation = self.process_generation(generation_data.id_)
            region.generation_key = generation.id
            region.main_generation = generation

        #if region not in self._session:
        #if inspect(region).detached:
        #    self._session.add(region) # need to add region to a session before we can acess the version_groups attribute
        #if region not in self._session:
        #    region = self._session.merge(region)
        """ for vg_data in region_data.version_groups:
            vg = self.process_version_group(vg_data.id_)
            #if vg not in self._session:
            #    vg = self._session.merge(vg)
            if vg not in region.version_groups:
                region.version_groups.append(vg) """

        return region
    
# Moves
    @api_resource(MoveBattleStyle)
    def process_move_battle_style(mbs: MoveBattleStyle, mbs_data: APIResource, self, id_: int, ignore_404: bool = False) -> MoveBattleStyle:
        return mbs
    
    @api_resource(DamageClass)
    def process_damage_class(dc: DamageClass, dc_data: APIResource, self, id_: int, ignore_404: bool = False) -> DamageClass:
        return dc
    
# Pokemon

    @api_resource(PokemonAbility)
    def process_ability(ability: PokemonAbility, ability_data, self, id_: int, ignore_404: bool = False) -> PokemonAbility:
        generation_id = ability_data.generation.id_
        generation = self.process_generation(generation_id)
        ability.generation = generation
        ability.generation_key = generation.id

        return ability
    
    @api_resource(PokemonCharacteristic)
    def process_characteristic(characteristic: PokemonCharacteristic, characteristic_data: APIResource, self, id_: int, ignore_404: bool = False) -> PokemonCharacteristic:
        highest_stat_data = characteristic_data.highest_stat
        highest_stat = self.process_stat(highest_stat_data.id_)
        # maybe not this:
        ## Just populate the key. We'll populate the relationship on the stat side
        ## Adding the relationship here will cascade the stat into the session, which we don't want yet
        characteristic.highest_stat = highest_stat
        characteristic.highest_stat_key = highest_stat.id

        return characteristic
        
    @api_resource(EggGroup)
    def process_egg_group(egg_group: EggGroup, egg_group_data, self, id_: int, ignore_404: bool = False) -> EggGroup:
        return egg_group
    
    @api_resource(GrowthRate)
    def process_growth_rate(growth_rate: GrowthRate, growth_rate_data, self, id_: int, ignore_404: bool = False) -> GrowthRate:
        for level_data in growth_rate_data.levels:
            level = self.process_growth_rate_exp_level(level_data, growth_rate_data.id_)

        return growth_rate
    
    def process_growth_rate_exp_level(self, level_data, growth_rate_id: int) -> GrowthRateExperienceLevel:

        processing_key = "GrowthRateExperienceLevel:"+str(growth_rate_id)+":"+str(level_data.level)
        if processing_key in self._processing:
            logger.debug("process_growth_rate_exp_level: growth rate exp level for GrowthRate: %s and level: %s already being processed", growth_rate_id, level_data.level)
            raise ProcessingInProgressException
        
        self._processing.add(processing_key)
        try:
            growth_rate = self.process_growth_rate(growth_rate_id)
            stmt = select(GrowthRateExperienceLevel).filter_by(growth_rate_key=growth_rate.id, level=level_data.level)
            with Session() as session:
                exp_level: GrowthRateExperienceLevel = session.scalars(stmt).first()
            if exp_level:
                exp_level.compare(level_data)
            else:
                exp_level = GrowthRateExperienceLevel.parse_data(level_data)
            
            exp_level.growth_rate = growth_rate
            exp_level.growth_rate_key = growth_rate.id

            with Session() as session:
                exp_level = session.merge(exp_level)
                session.commit()

        finally:
            self._processing.remove(processing_key)
        
        return exp_level

    @api_resource(PokemonNature)
    def process_nature(nature: PokemonNature, nature_data: APIResource, self, id_: int, ignore_404: bool = False) -> PokemonNature:
    
        for pokeathlon_stat_data in nature_data.pokeathlon_stat_changes:
            max_change = pokeathlon_stat_data.max_change
            pokeathlon_stat = self.process_pokeathlon_stat(pokeathlon_stat_data.pokeathlon_stat.id_)
            if max_change < 0:
                nature.max_pokeathlon_decrease = max_change
                nature.decreased_pokeathlon_stat = pokeathlon_stat
                nature.decreased_pokeathlon_stat_key = pokeathlon_stat.id
            else:
                nature.max_pokeathlon_increase = max_change
                nature.increased_pokeathlon_stat = pokeathlon_stat
                nature.increased_pokeathlon_stat_key = pokeathlon_stat.id

        hates_flavor_data = nature_data.hates_flavor
        hates_flavor = self.process_berry_flavor(hates_flavor_data.id_)
        nature.hates_flavor = hates_flavor
        nature.hates_flavor_key = hates_flavor.id

        likes_flavor_data = nature_data.likes_flavor
        likes_flavor = self.process_berry_flavor(likes_flavor_data.id_)
        nature.likes_flavor = likes_flavor
        nature.likes_flavor_key = likes_flavor.id

        for mbsp_data in nature_data.move_battle_style_preferences:
            mbsp = self.process_move_battle_style_pref(mbsp_data, nature)
            #nature.move_battle_style_preferences.append(mbsp)

        # Process Stats last
        # Processing stats will cascade the Nature into the session
        # Need to make sure that the other links have already been processed

        decreased_stat_data = nature_data.decreased_stat
        decreased_stat = self.process_stat(decreased_stat_data.id_)
        nature.decreased_stat = decreased_stat
        nature.decreased_stat_key = decreased_stat.id

        increased_stat_data = nature_data.increased_stat
        increased_stat = self.process_stat(increased_stat_data.id_)
        nature.increased_stat = increased_stat
        nature.increased_stat_key = increased_stat.id

        return nature

    def process_move_battle_style_pref(self,mbsp_data, nature: PokemonNature) -> MoveBattleStylePreference:

        processing_key = "MoveBattleStylePreference:"+str(nature.poke_api_id)+":"+str(mbsp_data.move_battle_style.id_)
        if processing_key in self._processing:
            logger.debug("process_move_battle_style_pref: move battle style pref for nature: %s and move battle style: %s already being processed", nature.poke_api_id, mbsp_data.move_battle_style.id_)
            raise ProcessingInProgressException
        
        self._processing.add(processing_key)
        try:
            mbs = self.process_move_battle_style(mbsp_data.move_battle_style.id_)
            stmt = select(MoveBattleStylePreference).filter_by(pokemon_nature_key=nature.id, move_battle_style_key=mbs.id)
            with Session() as session:
                mbsp: MoveBattleStylePreference = session.scalars(stmt).first()
            if mbsp:
                mbsp.compare(mbsp_data)
            else:
                mbsp = MoveBattleStylePreference.parse_data(mbsp_data)
            
            mbsp.pokemon_nature = nature
            mbsp.pokemon_nature_key = nature.id

            mbsp.move_battle_style = mbs
            mbsp.move_battle_style_key = mbs.id
            with Session() as session:
                mbsp = session.merge(mbsp)
                session.commit()

        finally:
            self._processing.remove(processing_key)
        
        return mbsp

    @api_resource(PokeathlonStat)
    def process_pokeathlon_stat(stat: PokeathlonStat, stat_data: APIResource, self, id_: int, ignore_404: bool = False) -> PokeathlonStat:
        return stat

    @api_resource(Pokemon)
    def process_pokemon(pokemon: Pokemon, pokemon_data: APIResource, self, id_: int, ignore_404: bool = False) -> Pokemon:

        # process stats
        for stat_data in pokemon_data.stats:
            stat = self.process_stat(stat_data.stat.id_)
            if stat.name == 'hp':
                pokemon.hp = stat_data.base_stat
                pokemon.hp_ev = stat_data.effort
            elif stat.name == 'attack':
                pokemon.attack = stat_data.base_stat
                pokemon.attack_ev = stat_data.effort
            elif stat.name == 'defense':
                pokemon.defense = stat_data.base_stat
                pokemon.defense_ev = stat_data.effort
            elif stat.name == 'special-attack':
                pokemon.special_attack = stat_data.base_stat
                pokemon.special_attack_ev = stat_data.effort
            elif stat.name == 'special-defense':
                pokemon.special_defense = stat_data.base_stat
                pokemon.special_defense_ev = stat_data.effort
            elif stat.name == 'speed':
                pokemon.speed = stat_data.base_stat
                pokemon.speed_ev = stat_data.effort
            else:
                logger.error("Unknown stat found: %s", stat.name)
                raise

        species_data = pokemon_data.species
        species = self.process_pokemon_species(species_data.id_)
        pokemon.species = species
        pokemon.species_key = species.id

        for type_data in pokemon_data.types:
            type_ = self.process_type(type_data.type.id_)
            if type_data.slot == 1:
                pokemon.type_1 = type_
                pokemon.type_1_key = type_.id
            else:
                pokemon.type_2 = type_
                pokemon.type_2_key = type_.id

        with Session() as session:
            pokemon = session.merge(pokemon)
            past_type_map: Dict[str, PastTypeLink] = {str(ptl.generation.poke_api_id) + ":" + str(ptl.type_1.poke_api_id) + ":" + str(ptl.type_2.poke_api_id): ptl for ptl in pokemon.past_types}
            if len(past_type_map) > 0:
                logger.debug("Process PastTypeLink: Found %s existing PastTypeLink entries for pokemon: %s", len(past_type_map), pokemon.name)
            for past_types_data in pokemon_data.past_types:
                generation_id = past_types_data.generation.id_
                generation = self.process_generation(generation_id)
                past_type_2_id = None
                for past_type_data in past_types_data.types:
                    if past_type_data.slot == 1:
                        past_type_1_id = past_type_data.type.id_
                        past_type_1 = self.process_type(past_type_1_id)
                    else:
                        past_type_2_id = past_type_data.type.id_
                        past_type_2 = self.process_type(past_type_2_id)


                map_key = str(generation_id) + ":" + str(past_type_1_id) + ":" + str(past_type_2_id)
                ptl = past_type_map.pop(map_key, None)

                if not ptl:
                    logger.debug("Process PastTypeLink: Parsing new PastTypeLink for pokemon: %s generation: %s types; %s & %s", pokemon_data.id, generation_id, past_type_1_id, past_type_2_id)
                    ptl = PastTypeLink()
                    ptl.pokemon = pokemon
                    ptl.pokemon_key = pokemon.id
                    ptl.last_generation = generation
                    ptl.last_generation_key = generation.id
                    ptl.type_1 = past_type_1
                    ptl.type_1_key = past_type_1.id
                    if past_type_2:
                        ptl.type_2 = past_type_2
                        ptl.type_2_key = past_type_2.id

        if past_type_map:
            logger.debug("Process PastTypeLink: Found %s existing PastTypeLink entries to be deleted for pokemon: %s", len(past_type_map), pokemon.name)
            ptl_ids_to_delete: List[int] = [ ptl.id for ptl in past_type_map.values() ]
            with Session() as session:
                session.execute(delete(PastTypeLink).where(PastTypeLink.id.in_(ptl_ids_to_delete)))
                session.commit()


        for ability_data in pokemon_data.abilities:
            ability = self.process_ability(ability_data.ability.id_)
            if ability_data.slot == 1:
                pokemon.ability_1 = ability
                pokemon.ability_1_key = ability.id
            elif ability_data.slot == 3:
                if not ability_data.is_hidden:
                    logger.error("process_ability: Found ability: %s with slot 3 that is not hidden ability", ability_data.ability.id_)
                    raise Exception("Ability with non-hidden slot 3")
                pokemon.hidden_ability = ability
                pokemon.hidden_ability_key = ability.id
            else:
                pokemon.ability_2 = ability
                pokemon.ability_2_key = ability.id

        for form_data in pokemon_data.forms:
            form = self.process_pokemon_form(form_data.id_)
    
        # Should be handled in decorator
        #game_indices: Mapped[List["PokemonGameIndex"]] = relationship(back_populates="object_ref",
        #                                    primaryjoin="Pokemon.id == foreign(PokemonGameIndex.object_key)")

        for held_item_data in pokemon_data.held_items:
            item = self.process_item(held_item_data.item.id_)
            for version_detail in held_item_data.version_details:
                held_item = self.process_held_item(pokemon=pokemon, item=item, version_detail=version_detail)

        for encounter_data in pokemon_data.location_area_encounters:
            area_id = encounter_data.location_area.id_
            for version_detail in encounter_data.version_details:
                pokemon_encounter = self.process_pokemon_encounter(version_detail, area_id, pokemon)

    
        #pokemon_encounters: Mapped[List["PokemonEncounter"]] = relationship(back_populates="pokemon",
        #                                    primaryjoin="Pokemon.id == foreign(PokemonEncounter.pokemon_key)")
    
        #moves: Mapped[List["PokemonMove"]] = relationship(back_populates="pokemon",
        #                                    primaryjoin="Pokemon.id == foreign(PokemonMove.pokemon_key)")

        return pokemon
    
    def process_held_item(self, pokemon: Pokemon, item: Item, version_detail):
        version_id = version_detail.version.id_
        rarity = version_detail.rarity
        processing_key = "PokemonHeldItem:"+str(pokemon.poke_api_id)+":"+str(item.poke_api_id)+":"+str(version_id)
        if processing_key in self._processing:
            logger.debug("process_held_item: held item for pokemon: %s and item: %s and version: already being processed", pokemon.poke_api_id, item.poke_api_id, version_id)
            raise ProcessingInProgressException
        
        self._processing.add(processing_key)
        try:
            version = self.process_version(version_id)
            stmt = select(PokemonHeldItem).filter_by(pokemon_key=pokemon.id, item_key=item.id, version_key=version.id)
            with Session() as session:
                held_item: PokemonHeldItem = session.scalars(stmt).first()
            if held_item:
                held_item.compare(rarity)
            else:
                held_item = PokemonHeldItem.parse_data(rarity)
            
            held_item.pokemon = pokemon
            held_item.pokemon_key = pokemon.id

            held_item.item = item
            held_item.item_key = item.id

            held_item.version = version
            held_item.version_key = version.id

            with Session() as session:
                held_item = session.merge(held_item)
                session.commit()

        finally:
            self._processing.remove(processing_key)

        return held_item
    
    @api_resource(PokemonForm)
    def process_pokemon_form(form: PokemonForm, form_data: APIResource, self, id_: int, ignore_404: bool = False) -> PokemonForm:
    
        pokemon: Pokemon = self.process_pokemon(form_data.pokemon.id_)
        form.pokemon = pokemon
        form.pokemon_key = pokemon.id

        for type_data in form_data.types:
            type_ = self.process_type(type_data.type.id_)
            if type_data.slot == 1:
                form.type_1 = type_
                form.type_1_key = type_.id
            elif type_data.slot == 2:
                form.type_2 = type_
                form.type_2_key = type_.id
            else:
                logger.error("Found Form with unexpected type slot: %s for form id: %s pokemon id: %s", type_data.slot, form_data.id_, pokemon.poke_api_id)
                raise Exception("PokemonForm type slot error")
    
        version_group = self.process_version_group(form_data.version_group.id_)
        form.version_group = version_group
        form.version_group_key = version_group.id
    
        return form
    
    @api_resource(PokemonSpecies)
    def process_pokemon_species(species: PokemonSpecies, species_data: APIResource, self, id_: int, ignore_404: bool = False) -> PokemonSpecies:
        #links = {}

        if species_data.evolves_from_species:
            evolves_from_species_id: int = species_data.evolves_from_species.id_
            evolves_from_species: PokemonSpecies = self.process_pokemon_species(evolves_from_species_id, ignore_404 = False)

            species.evolves_from_species = evolves_from_species
            species.evolves_from_species_key = evolves_from_species.id

            #links['evolves_from_species_key'] = evolves_from_species.id
            #links['evolves_from_species'] = evolves_from_species

        # varieties
        for variety in species_data.varieties:
            pokemon_id = variety.pokemon.id_
            pokemon = self.process_pokemon(pokemon_id)
            #species.varieties.append(pokemon)


        #egg_groups = []
        egg_group_1_id = species_data.egg_groups[0].id_
        egg_group_1 = self.process_egg_group(egg_group_1_id)

        species.egg_group_1 = egg_group_1
        species.egg_group_1_key = egg_group_1.id
        #egg_groups.append(egg_group_1)
        if len(species_data.egg_groups) > 1:
            egg_group_2_id = species_data.egg_groups[1].id_
            egg_group_2 = self.process_egg_group(egg_group_2_id)
            #egg_groups.append(egg_group_2)

            species.egg_group_2 = egg_group_2
            species.egg_group_2_key = egg_group_2.id

        #color
        color_id = species_data.color.id_
        color = self.process_pokemon_color(color_id)
        species.color = color
        species.color_key = color.id

        #shape
        shape_id = species_data.shape.id_
        shape = self.process_pokemon_shape(shape_id)
        species.shape = shape
        species.shape_key = shape.id

        #habitat
        habitat_id = species_data.habitat.id_
        habitat = self.process_pokemon_habitat(habitat_id)
        species.habitat = habitat
        species.habitat_key = habitat.id

        #evolution chain
        evolution_chain_id = species_data.evolution_chain.id
        evolution_chain = self.process_evolution_chain(evolution_chain_id)
        species.evolution_chain = evolution_chain
        species.evolution_chain_key = evolution_chain.id

        growth_rate_data = species_data.growth_rate
        growth_rate = self.process_growth_rate(growth_rate_data.id_)
        species.growth_rate = growth_rate
        species.growth_rate_key = growth_rate.id

        generation_data = species_data.generation
        generation = self.process_generation(generation_data.id_)
        species.generation = generation
        species.generation_key = generation.id


        for pal_park_data in species_data.pal_park_encounters:
            pal_park_encounter = self.process_pal_park_encounter(pal_park_data, species)

        # Should be handled as a TextEntry
        #genera: Mapped[List["PokemonGenus"]] = relationship(back_populates="object_ref",
        #                                              primaryjoin="PokemonSpecies.id == foreign(PokemonGenus.object_key)")



        return species

    @api_resource(PokemonColor)
    def process_pokemon_color(color: PokemonColor, color_data: APIResource, self, id_: int, ignore_404: bool = False) -> PokemonColor:
        return color
    
    @api_resource(PokemonShape)
    def process_pokemon_shape(shape: PokemonShape, shape_data: APIResource, self, id_: int, ignore_404: bool = False) -> PokemonShape:
        return shape

    @api_resource(PokemonHabitat)
    def process_pokemon_habitat(habitat: PokemonHabitat, habitat_data: APIResource, self, id_: int, ignore_404: bool = False) -> PokemonHabitat:
        return habitat
    
    @api_resource(PokemonStat)
    def process_stat(stat: PokemonStat, stat_data: APIResource, self, id_: int, ignore_404: bool = False, skip_nature: bool = False) -> PokemonStat:
        damage_class_data = stat_data.move_damage_class
        if damage_class_data:
            damage_class_id = damage_class_data.id_
            damage_class = self.process_damage_class(damage_class_id)
            stat.damage_class = damage_class
            stat.damage_class_key = damage_class.id

        for characteristic_data in stat_data.characteristics:
            characteristic = self.process_characteristic(characteristic_data.id_)
            #stat.characteristics.append(characteristic)

        if not skip_nature:
            for nature_data in stat_data.affecting_natures.decrease:
                nature = self.process_nature(nature_data.id_)
                #stat.decreasing_natures.append(nature)

            for nature_data in stat_data.affecting_natures.increase:
                nature = self.process_nature(nature_data.id_)
                #stat.increasing_natures.append(nature)
    
        return stat
    
    @api_resource(PokemonType)
    def process_type(type_: PokemonType, type_data: APIResource, self, id_: int, ignore_404: bool = False) -> PokemonType:
        #logger.error("TESTING: in process_type before process_generation for id_: %s current identity_map: %s", id_, self._session.identity_map.items())
        generation_data = type_data.generation
        generation = self.process_generation(generation_data.id_)
        #logger.error("TESTING: in process_type after process_generation for id_: %s current identity_map: %s", id_, self._session.identity_map.items())
        type_.generation_introduced = generation
        type_.generation_introduced_key = generation.id
        #logger.error("TESTING: in process_type after type_.generation_introd for id_: %s current identity_map: %s", id_, self._session.identity_map.items())

        logger.debug("process_type: process damage class for type id_: %s name: %s", id_, type_.name)
        damage_class_data = type_data.move_damage_class
        # Fairy doesn't have a damage class
        if damage_class_data:
            damage_class = self.process_damage_class(damage_class_data.id_)
            type_.damage_class = damage_class
            type_.damage_class_key = damage_class.id
        #logger.error("TESTING: in process_type after damageclass for id_: %s current identity_map: %s", id_, self._session.identity_map.items())


        for off_type in type_data.damage_relations.double_damage_from:
            self.process_type_relation(offensive_type_id = off_type.id_, defensive_type_id = type_.poke_api_id, damage_multiplier = 2.0)
        for def_type in type_data.damage_relations.double_damage_to:
            self.process_type_relation(offensive_type_id = type_.poke_api_id, defensive_type_id = def_type.id_, damage_multiplier = 2.0)

        for off_type in type_data.damage_relations.half_damage_from:
            self.process_type_relation(offensive_type_id = off_type.id_, defensive_type_id = type_.poke_api_id, damage_multiplier = 0.5)
        for def_type in type_data.damage_relations.half_damage_to:
            self.process_type_relation(offensive_type_id = type_.poke_api_id, defensive_type_id = def_type.id_, damage_multiplier = 0.5)

        for off_type in type_data.damage_relations.no_damage_from:
            self.process_type_relation(offensive_type_id = off_type.id_, defensive_type_id = type_.poke_api_id, damage_multiplier = 0.0)
        for def_type in type_data.damage_relations.no_damage_to:
            self.process_type_relation(offensive_type_id = type_.poke_api_id, defensive_type_id = def_type.id_, damage_multiplier = 0.0)

        for past_damage_relation in type_data.past_damage_relations:
            generation_id = past_damage_relation.generation.id_

            for off_type in past_damage_relation.damage_relations.double_damage_from:
                self.process_type_relation(offensive_type_id = off_type.id_, defensive_type_id = type_.poke_api_id, damage_multiplier = 2.0, generation_id = generation_id)
            for def_type in past_damage_relation.damage_relations.double_damage_to:
                self.process_type_relation(offensive_type_id = type_.poke_api_id, defensive_type_id = def_type.id_, damage_multiplier = 2.0, generation_id = generation_id)

            for off_type in past_damage_relation.damage_relations.half_damage_from:
                self.process_type_relation(offensive_type_id = off_type.id_, defensive_type_id = type_.poke_api_id, damage_multiplier = 0.5, generation_id = generation_id)
            for def_type in past_damage_relation.damage_relations.half_damage_to:
                self.process_type_relation(offensive_type_id = type_.poke_api_id, defensive_type_id = def_type.id_, damage_multiplier = 0.5, generation_id = generation_id)

            for off_type in past_damage_relation.damage_relations.no_damage_from:
                self.process_type_relation(offensive_type_id = off_type.id_, defensive_type_id = type_.poke_api_id, damage_multiplier = 0.0, generation_id = generation_id)
            for def_type in past_damage_relation.damage_relations.no_damage_to:
                self.process_type_relation(offensive_type_id = type_.poke_api_id, defensive_type_id = def_type.id_, damage_multiplier = 0.0, generation_id = generation_id)

        
        """ gi_entry_map: Dict[str, GenerationGameIndex] = {str(type_.poke_api_id) + ":" + str(gi.generation.poke_api_id) + ":" + str(gi.game_index): gi for gi in type_.game_indices}
        if len(gi_entry_map) > 0:
            logger.debug("Process GenerationGameIndex: Found %s existing GameIndex entries for type: %s", len(gi_entry_map), type_.name)
        
        for gi_data in type_data.game_indices:
            game_index = gi_data.game_index
            generation_id = gi_data.generation.id_
            generation = self.process_generation(generation_id)

            map_key = str(type_data.id) + ":" + str(generation_id) + ":" + str(game_index) #object_id:generation_id:game_index
            gi = gi_entry_map.pop(map_key, None)

            if not gi:
                logger.debug("Process GenerationGameIndex: Parsing new GameIndex for type: %s generation: %s game_index; %s", type_data.id, generation_id, game_index)
                tgi = TypeGameIndex(game_index)
                tgi.generation = generation
                tgi.generation_key = generation.id
                tgi.object_key = type_.id
                tgi.object_ref = type_

        if gi_entry_map:
            logger.debug("Process GenerationGameIndex: Found %s existing TypeGameIndex entries to be deleted for type: %s", len(gi_entry_map), type_.poke_api_id)
            gi_ids_to_delete: List[int] = [ gi.id for gi in gi_entry_map.values() ]
            self._session.execute(delete(TypeGameIndex).where(TypeGameIndex.id.in_(gi_ids_to_delete))) """

        return type_


    def process_type_relation(self,offensive_type_id: int, defensive_type_id: int, damage_multiplier: float, generation_id: int = None) -> PokemonTypeRelation:
        #logger.error("TESTING: in process_type_relation for off_type: %s def_type: %s mult: %s generation: %s", offensive_type_id, defensive_type_id, damage_multiplier, generation_id)
        #logger.error("TESTING: in process_type_relation before off_type current identity_map: %s", self._session.identity_map.items())
        off_type = self.process_type(offensive_type_id)
        #logger.error("TESTING: in process_type_relation before def_type current identity_map: %s", self._session.identity_map.items())
        def_type = self.process_type(defensive_type_id)
        #logger.error("TESTING: in process_type_relation before process_generation current identity_map: %s", self._session.identity_map.items())
        generation = None
        if generation_id:
            generation = self.process_generation(generation_id)

        #logger.error("TESTING: in process_type_relation after process_generation current identity_map: %s", self._session.identity_map.items())
        #should we get relation from cache???
        
        processing_key = "PokemonTypeLink:"+str(offensive_type_id)+":"+str(defensive_type_id)+":"+str(generation_id)
        if processing_key in self._processing:
            logger.debug("process_type_relation: type relations for offensive type: %s defensive type: %s and generation: %s already being processed", offensive_type_id, defensive_type_id, generation_id)
            raise ProcessingInProgressException
        
        self._processing.add(processing_key)
        try:
            if generation:
                stmt = select(PokemonTypeRelation).filter_by(offensive_type_key=off_type.id, defensive_type_key=def_type.id, generation_key=generation.id)
            else:
                stmt = select(PokemonTypeRelation).filter_by(offensive_type_key=off_type.id, defensive_type_key=def_type.id, generation_key=None)
            with Session() as session:
                relation: PokemonTypeRelation = session.scalars(stmt).first()
            if relation:
                relation.compare(damage_multiplier=damage_multiplier)
            else:
                relation = PokemonTypeRelation.parse_data(damage_multiplier=damage_multiplier)

            if relation.offensive_type_key != off_type.id:
                relation.offensive_type = off_type
                relation.offensive_type_key = off_type.id
            if relation.defensive_type_key != def_type.id:
                relation.defensive_type = def_type
                relation.defensive_type_key = def_type.id

            #logger.error("TESTING: in process_type_relation before relation.generation current identity_map: %s", self._session.identity_map.items())
            if generation and relation.generation_key != generation.id:
                relation.generation = generation
                relation.generation_key = generation.id
                
            #logger.error("TESTING: in process_type_relation after relation.generation current identity_map: %s", self._session.identity_map.items())
            with Session() as session:
                relation = session.merge(relation)
                session.commit()

            #self._session.merge(relation)
            #self._session.commit()

        finally:
            self._processing.remove(processing_key)
        
        return relation

 # TextEntry

    @api_resource(Language)
    def process_language(language, language_data, self, language_id: int, ignore_404: bool = False) -> "Language":
        return language

    def process_pokemon_species_old(self, species_id: int) -> PokemonSpecies: 
        logger.debug("process_pokemon_species: species_id: %s", species_id)
        species, needs_update = PokemonSpecies.get_from_cache(species_id)
        if species:
            logger.debug("process_pokemon_species: got from cache: %s, needs_update: %s", species.name, needs_update)
        else:
            logger.debug("process_pokemon_species: species_id: %s not in cache, retrieving from api", species_id)
        if needs_update:
            species_data = self.get_species_data(species_id)
            api_url = species_data.url
            if api_url in self._processing:
                logger.debug("process_pokemon_species: species_id: %s already being processed", species_id)
                raise ProcessingInProgressException

            self._processing.add(api_url)

            try:

                #nat_dex = species_data.id
                links = {}

                if species_data.evolves_from_species:
                    evolves_from_species_id: int = species_data.evolves_from_species.id_
                    evolves_from_species = self.process_pokemon_species(evolves_from_species_id)

                    links['evolves_from_species_key'] = evolves_from_species.id
                    links['evolves_from_species'] = evolves_from_species

                egg_groups = []
                egg_group_1_id = species_data.egg_groups[0].id_
                egg_group_1 = self.process_egg_group(egg_group_1_id)
                egg_groups.append(egg_group_1)
                if len(species_data.egg_groups) > 1:
                    egg_group_2_id = species_data.egg_groups[1].id_
                    egg_group_2 = self.process_egg_group(egg_group_2_id)
                    egg_groups.append(egg_group_2)

                





                species = PokemonSpecies.get_species(species_id)
                if species:
                    species.compare(species_data)
                else:
                    species = PokemonSpecies.parse_species(species_data)
            finally:
                self._processing.remove(api_url)

            return Language
        
    """ def process_api_resource(self, T: Type[PokeApiResource], id_: int, ignore_404: bool = False) -> PokeApiResource:
        type_name = T.__tablename__
        logger.debug("Process %s: id_: %s", type_name, id_)

        api_object, needs_update = T.get_from_cache(id_)
        if api_object:
            logger.debug("Process %s: got from cache: %s, needs_update: %s", type_name, api_object.id_, needs_update)
        else:
            logger.debug("Process %s: id_: %s not in cache, retrieving from api", type_name, id_)
        if needs_update:
            object_data = self.get_object_data(T, id_, ignore_404)
            api_url = object_data.url
            if api_url in self._processing:
                logger.debug("Process %s: id_: %s already being processed", type_name, id_)
                raise ProcessingInProgressException

            self._processing.add(api_url)

            try:
                if api_object:
                    logger.debug("Process %s: Comparing existing object to API data for id: %s", type_name, id_)
                    api_object.compare(object_data)
                else:
                    logger.debug("Process %s: id_: %s not in cache, retrieving from api", type_name, id_)
                    api_object = T.parse_data(object_data)

                #links

                self._session.add(api_object)

                #other links

                self._session.commit()

            finally:
                self._processing.remove(api_url)

        return api_object """

    def process_egg_group_old(self, egg_group_id: int, ignore_404: bool = False) -> EggGroup:
        logger.debug("process_egg_group: egg_group_id: %s", egg_group_id)
        egg_group, needs_update = EggGroup.get_from_cache(egg_group_id)
        if egg_group:
            logger.debug("process_egg_group: got from cache: %s, needs_update: %s", egg_group.name, needs_update)
        else:
            logger.debug("process_egg_group: egg_group_id: %s not in cache, retrieving from api", egg_group_id)
        if needs_update:
            #egg_group_data = self.get_egg_group_data(egg_group_id)
            egg_group_data = self.get_object_data(EggGroup, egg_group_id, ignore_404)
            api_url = egg_group_data.url
            if api_url in self._processing:
                logger.debug("process_egg_group: egg_group_id: %s already being processed", egg_group_id)
                raise ProcessingInProgressException

            self._processing.add(api_url)

            try:

                #poke_api_id = egg_group_data.id_
                #egg_group = EggGroup.get_egg_group(poke_api_id)
                if egg_group:
                    logger.debug("process_egg_group: Comparing existing EggGroup to API data for: %s", egg_group.name)
                    egg_group.compare(egg_group_data)
                else:
                    logger.debug("process_egg_group: egg_group_id: %s not in cache, retrieving from api", egg_group_id)
                    egg_group = EggGroup.parse_egg_group(egg_group_data)

                self._session.add(egg_group)

                self.process_names(egg_group, egg_group_data)

                """ logger.debug("process_egg_group: Processing EggGroupNames for EggGroup: %s", egg_group.name)
                if egg_group.names:
                    ### Leads to duplicates when text is the same for two different languages

                    name_map: Dict[str, "EggGroupName"] = { egg_group_name.text_entry + str(egg_group_name.language.poke_api_id) : egg_group_name for egg_group_name in egg_group.names }
                    logger.debug("process_egg_group: Found %s existing EggGroupNames for EggGroup: %s", len(name_map), egg_group.name)
                else:
                    name_map = {}
                
                for name_data in egg_group_data.names:
                    name_key = name_data.name + str(name_data.language.id_)
                    name = name_map.pop(name_key, None)

                    #names: List["EggGroupName"] = []
                    #for name_data in egg_group_data.names:
                    if not name:
                        logger.debug("process_egg_group: Parsing new EggGroupName: %s", name_data.name)
                        egg_group_name = EggGroupName(name_data)
                        egg_group_name.object_key = egg_group.id
                        egg_group_name.object_ref = egg_group

                        egg_group_name_language = self.process_language(name_data.language.id_)
                        egg_group_name.language = egg_group_name_language
                        egg_group_name.language_key = egg_group_name_language.id

                        self._session.add(egg_group_name)

                    #names.append(egg_group_name)
                #egg_group.names = names

                remaining_names = len(name_map)
                if remaining_names>0:
                    logger.debug("process_egg_group: Found %s existing EggGroupNames to be deleted for EggGroup: %s", remaining_names, egg_group.name)
                    for name_to_delete in name_map:
                        logger.debug("process_egg_group: Deleting EggGroupNames: %s", name_to_delete)
                    name_ids_to_delete: List[int] = [ name.id for name in name_map.values() ]
                    self._session.execute(delete(EggGroupName).where(EggGroupName.id.in_(name_ids_to_delete))) """

                #self._session.add(egg_group)
                self._session.commit()

            finally:
                self._processing.remove(api_url)

        return egg_group

    """ @rate_limit
    def get_egg_group_data(self, egg_group_id: int) -> APIResource:
        egg_group_data = None
        try: 
            egg_group_data = pokebase.egg_group(egg_group_id)
        except HTTPError as ex:
            if ex.response.status_code != 404:
                raise ex
            #else:
            #    return None
        return egg_group_data """
    

    
    def process_language_old(self, language_id: int, ignore_404: bool = False) -> "Language":
        logger.debug("process_language: language_id: %s", language_id)
        language, needs_update = Language.get_from_cache(language_id)
        if language:
            logger.debug("process_language: got from cache: %s, needs_update: %s", language.name, needs_update)
        else:
            logger.debug("process_language: language_id: %s not in cache, retrieving from api", language_id)
        if needs_update:
            #language_data = self.get_language_data(language_id)
            language_data = self.get_object_data(Language, language_id, ignore_404)
            api_url = language_data.url
            if api_url in self._processing:
                logger.debug("process_language: language_id: %s already being processed", language_id)
                raise ProcessingInProgressException

            self._processing.add(api_url)
            try:
            #poke_api_id = language_data.id_
            #language, needs_update = Language.get_from_cache(poke_api_id)
            #if needs_update:
                if language:
                    logger.debug("process_language: Comparing existing Language to API data for: %s", language.name)
                    language.compare(language_data)
                else:
                    logger.debug("process_language: Parsing new Language from API data for %s", language_data.name)
                    language = Language.parse_langauge(language_data)

                self._session.add(language)

                #names: List["LanguageName"] = language.names
                #names: List["LanguageName"] = []

                self.process_names(language, language_data)

                """ logger.debug("process_language: Processing LanguageNames for Language: %s", language.name)
                if language.names:
                    name_map: Dict[str, "LanguageName"] = { language_name.text_entry : language_name for language_name in language.names }
                    logger.debug("process_language: Found %s existing LanguageNames for Language: %s", len(name_map), language.name)
                else:
                    name_map = {}
                
                for name_data in language_data.names:
                    name = name_map.pop(name_data.name, None)

                    #if name:
                    #    names.append(name_map.get(name_data.name))
                    #else:
                    if not name:
                        logger.debug("process_language: Parsing new LanguageName: %s", name_data.name)
                        language_name = LanguageName(name_data)
                        language_name.object_key = language.id
                        language_name.object_ref = language

                        #Recursively process language
                        language_name_language = self.process_language(name_data.language.id_)
                        language_name.language = language_name_language
                        language_name.language_key = language_name_language.id
                        self._session.add(language_name)

                        #names.append(language_name)
                        #name_map[language_name.text_entry] = language_name
                    #language.names = names
                remaining_names = len(name_map)
                if remaining_names>0:
                    logger.debug("process_language: Found %s existing LanguageNames to be deleted for Language: %s", remaining_names, language.name)
                    for name_to_delete in name_map:
                        logger.debug("process_language: Deleting LanguageName: %s", name_to_delete)
                    name_ids_to_delete: List[int] = [ name.id for name in name_map.values() ]
                    self._session.execute(delete(LanguageName).where(LanguageName.id.in_(name_ids_to_delete))) """

                self._session.commit()

            finally:
                self._processing.remove(api_url)

        return language

    """ @rate_limit
    def get_language_data(self, language_id: int) -> APIResource:
        language_data = None
        try:
            language_data = pokebase.language(language_id)
        except HTTPError as ex:
            if ex.response.status_code != 404:
                raise ex

        return language_data """
    
    """ def process_names(self, object: PokeApiResource, object_data: APIResource):
        object_class = inspect(object).mapper.class_
        name_class = inspect(object).mapper.relationships.names.mapper.class_
        if object.names:
            name_map: Dict[str, TextEntry] = { name.text_entry + str(name.language.poke_api_id): name for name in object.names }
            logger.debug("process_names: Found %s existing names for %s: %s", len(name_map), object_class.__tablename__, object.name)
        else:
            name_map = {}
                
            for name_data in object_data.names:
                name_key = name_data.name + str(name_data.language.id_)
                name = name_map.pop(name_key, None)

                if not name:
                    logger.debug("process_names: Parsing new name: %s", name_data.name)
                    object_name = name_class(name_data)
                    object_name.object_key = object.id
                    object_name.object_ref = object

                    #Recursively process language
                    language_name_language = self.process_language(name_data.language.id_, ignore_404=False)
                    object_name.language = language_name_language
                    object_name.language_key = language_name_language.id
                    self._session.add(object_name)

            remaining_names = len(name_map)
            if remaining_names>0:
                logger.debug("process_names: Found %s existing names to be deleted for %s: %s", remaining_names, object_class.__tablename__, object.name)
                for name_to_delete in name_map:
                    logger.debug("process_names: Deleting name: %s", name_to_delete)
                name_ids_to_delete: List[int] = [ name.id for name in name_map.values() ]
                self._session.execute(delete(name_class).where(name_class.id.in_(name_ids_to_delete))) """

    #def process_text_entries(self, )