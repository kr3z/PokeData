import time
import logging
from typing import Callable, List, TYPE_CHECKING, Dict, Type

from sqlalchemy import delete, inspect
from requests.exceptions import HTTPError
import pokebase
from pokebase.interface import APIResource

from Base import Session, PokeApiResource
from Berries import Berry
from Contests import ContestChain
from Evolution import EvolutionChain
from Encounters import Encounter
from Games import Generation
from Items import Item
from Locations import Region, Location
from Moves import Move, MoveLearnMethod, Machine
from Pokemon import PokemonSpecies, EggGroup, PokemonColor, PokemonShape
from TextEntries import EggGroupName, Language, LanguageName, TextEntry

logger = logging.getLogger('PokeBase')
REQ_WAIT_TIME = 1000

class ProcessingInProgressException(Exception):
    pass

POKEBASE_API: Dict[Type[PokeApiResource], Callable] = {
    PokemonSpecies: pokebase.pokemon_species,
    EggGroup: pokebase.egg_group,
    Language: pokebase.language,
    PokemonColor: pokebase.pokemon_color, 
    PokemonShape: pokebase.pokemon_shape
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

                    ret = func(api_object, object_data, self,*args, **kwargs)

                    self._session.add(api_object)

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
                        text_entry_map: Dict[str, TextEntry] = { text_entry.text_entry + str(text_entry.language.poke_api_id): text_entry for text_entry in  text_attr}
                        if len(text_entry_map) > 0:
                            logger.debug("Process %s: Found %s existing TextEntries for %s: %s", type_name, len(text_entry_map), type_name, text_relationship_name)

                        for text_data in data_attr:
                            text_key = getattr(text_data, text_class.text_entry_name) + str(text_data.language.id_)
                            text_entry = text_entry_map.pop(text_key, None)

                            if not text_entry:
                                logger.debug("Process %s: Parsing new TextEntry: %s", type_name, text_key)
                                object_text = text_class(text_data)
                                object_text.object_key = api_object.id
                                object_text.object_ref = api_object

                                #Recursively process language
                                object_text_language = self.process_language(text_data.language.id_, ignore_404=False)
                                object_text.language = object_text_language
                                object_text.language_key = object_text_language.id
                                self._session.add(object_text)

                        remaining_text_entries = len(text_entry_map)
                        if remaining_text_entries > 0:
                            logger.debug("Process %s: Found %s existing TextEntries to be deleted for %s: %s", remaining_text_entries, type_name, api_object.id)
                            for text_to_delete in text_entry_map:
                                logger.debug("Process %s: Deleting TextEntry: %s", type_name, text_to_delete)
                            text_ids_to_delete: List[int] = [ text_entry.id for text_entry in text_entry_map.values() ]
                            self._session.execute(delete(text_class).where(text_class.id.in_(text_ids_to_delete)))

                    #if hasattr(T, 'names'):
                    #    self.process_names(api_object, object_data)

                    #if hasattr(T, 'awesome_names'):


                    self._session.commit()

                finally:
                    self._processing.remove(api_url)

            return api_object

        return process_api_resource
    return api_resource_wrapper

class PokeBaseWrapper:
    _last_req: int = 0

    def __init__(self):
        self._session = Session()
        self._processing = set()

    def close(self):
        self._session.close()

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
    
    @api_resource(PokemonSpecies)
    def process_pokemon_species(species: PokemonSpecies, species_data: APIResource, self, species_id: int, ignore_404: bool = False) -> PokemonSpecies:
        #links = {}

        if species_data.evolves_from_species:
            evolves_from_species_id: int = species_data.evolves_from_species.id_
            evolves_from_species: PokemonSpecies = self.process_pokemon_species(evolves_from_species_id, ignore_404 = False)

            species.evolves_from_species = evolves_from_species
            species.evolves_from_species_key = evolves_from_species.id

            #links['evolves_from_species_key'] = evolves_from_species.id
            #links['evolves_from_species'] = evolves_from_species

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

        return species

    @api_resource(PokemonColor)
    def process_pokemon_color(color: PokemonColor, color_data: APIResource, self, color_id: int, ignore_404: bool = False) -> PokemonColor:
        return color
    
    @api_resource(PokemonShape)
    def process_pokemon_shape(shape: PokemonShape, shape_data: APIResource, self, shape_id: int, ignore_404: bool = False) -> PokemonShape:
        return shape

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
    
    @api_resource(EggGroup)
    def process_egg_group(egg_group, egg_group_data, self, egg_group_id: int, ignore_404: bool = False) -> EggGroup:
        return egg_group

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
    
    @api_resource(Language)
    def process_language(language, language_data, self, language_id: int, ignore_404: bool = False) -> "Language":
        return language
    
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
    
    def process_names(self, object: PokeApiResource, object_data: APIResource):
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
                self._session.execute(delete(name_class).where(name_class.id.in_(name_ids_to_delete)))

    #def process_text_entries(self, )