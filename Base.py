import os
import logging
import logging.config
import configparser
from typing import List, Optional, Tuple

from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from sqlalchemy import create_engine, Sequence, URL, event, text, String, Integer, SmallInteger, Table, Column, ForeignKey, select
from sqlalchemy.dialects import mysql

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(WORKING_DIR+os.sep+'config.properties')

logging.config.fileConfig(WORKING_DIR+os.sep+'logging.conf')
logger = logging.getLogger('DB')


db_host=config.get("db", "db_host")
db_name=config.get("db", "db_name")
db_user=config.get("db", "user")
db_password=config.get("db", "password")

sqlalchemy_url = URL.create(
    "mysql+mysqldb",
    username=db_user,
    password=db_password,
    host=db_host,
    database=db_name,
)

utf8mb4_1000 = String(1000).with_variant(mysql.VARCHAR(1000,collation='utf8mb4_unicode_520_ci'), 'mysql','mariadb')
utf8mb4_200 = String(200).with_variant(mysql.VARCHAR(200,collation='utf8mb4_unicode_520_ci'), 'mysql','mariadb')

TinyInteger = SmallInteger().with_variant(mysql.TINYINT, 'mysql','mariadb')
MediumInteger = Integer().with_variant(mysql.MEDIUMINT, 'mysql','mariadb')

class Base(DeclarativeBase):
    pass

engine = create_engine(sqlalchemy_url, pool_pre_ping=True, isolation_level="READ COMMITTED")
#engine = create_engine(sqlalchemy_url, pool_pre_ping=True, echo=True, isolation_level="READ COMMITTED")

@event.listens_for(engine, "connect", insert=True)
def connect(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET sql_mode = 'TRADITIONAL,NO_ENGINE_SUBSTITUTION'")

Session = sessionmaker(engine)

id_seq = Sequence("id_seq",metadata=Base.metadata, start=1, increment=1000, cache=10)

_id_pool = []

def get_next_id() -> int:
    if(len(_id_pool) == 0):
        logger.info("id pool empty, querying for more")
        fill_pool()
    return _id_pool.pop(0)
    
def get_ids(nIds: int) -> List[int]:
    while len(_id_pool)<nIds:
        fill_pool()
    ret_ids = _id_pool[0:nIds]
    del _id_pool[0:nIds]
    return ret_ids
    
def fill_pool() -> None:
    #conn = cls.getConnection()
    #res = conn.executeQuery("SELECT NEXTVAL(id_seq),increment from id_seq")
    with Session() as session:
        res = session.execute(text("SELECT NEXTVAL(id_seq),increment from id_seq")).first()
        #res = cls.singleQuery("SELECT NEXTVAL(id_seq),increment from id_seq")
        next_val = res[0]
        increment = res[1]
        logger.debug("Adding values %d to %d to id pool"  % (next_val,next_val+increment))
        _id_pool.extend(range(next_val,next_val+increment))

RegionToVersionGroupLink = Table(
    "RegionToVersionGroupLink",
    Base.metadata,
    Column("region_key", ForeignKey("Region.id"), primary_key=True),
    Column("version_group_key", ForeignKey("VersionGroup.id"), primary_key=True),
)

PokedexToVersionGroupLink = Table(
    "PokedexToVersionGroupLink",
    Base.metadata,
    Column("pokedex_key", ForeignKey("Pokedex.id"), primary_key=True),
    Column("version_group_key", ForeignKey("VersionGroup.id"), primary_key=True),
)

MoveLearnMethodToVersionGroupLink = Table(
    "MoveLearnMethodToVersionGroupLink",
    Base.metadata,
    Column("move_learn_method_key", ForeignKey("MoveLearnMethod.id"), primary_key=True),
    Column("version_group_key", ForeignKey("VersionGroup.id"), primary_key=True),
)

EncounterToEncounterCondValLink = Table(
    "EncounterToEncounterCondValLink",
    Base.metadata,
    Column("encounter_key", ForeignKey("Encounter.id"), primary_key=True),
    Column("condition_value_key", ForeignKey("EncounterConditionValue.id"), primary_key=True),
)

ItemToItemAttributeLink = Table(
    "ItemToItemAttributeLink",
    Base.metadata,
    Column("item_key", ForeignKey("Item.id"), primary_key=True),
    Column("item_attribute_key", ForeignKey("ItemAttribute.id"), primary_key=True),
)

class PokeApiResource:
    poke_api_id: Mapped[int] = mapped_column(Integer)

    @classmethod
    def get_from_cache(cls, cache_key: int) -> Tuple[Optional["PokeApiResource"], bool]:
        needs_update = False
        if cache_key not in cls._cache:
            with Session() as session:
                needs_update = True
                cache_object = session.scalars(select(cls).filter_by(poke_api_id=cache_key)).first()
                if cache_object:
                    cls._cache[cache_object.poke_api_id] = cache_object
        return cls._cache.get(cache_key), needs_update