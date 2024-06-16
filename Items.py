from typing import List, Optional, TYPE_CHECKING, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, Table, Column, ForeignKey, UniqueConstraint

from Base import Base, ItemToItemAttributeLink, PokeApiResource, get_next_id

if TYPE_CHECKING:
    from Berries import Berry
    from Evolution import EvolutionChain, EvolutionDetail
    from Games import ItemGameIndex
    from Moves import Machine
    from Pokemon import PokemonHeldItem
    from TextEntries import ItemFlavorText, ItemEffect, ItemName, ItemAttributeName, ItemAttributeDescription
    from TextEntries import ItemFlingEffectEffect, ItemFlingEffectName, ItemCategoryName, ItemPocketName

class Item(Base, PokeApiResource):
    __tablename__ = "Item"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    cost: Mapped[int] = mapped_column(Integer)
    fling_power: Mapped[Optional[int]] = mapped_column(SmallInteger)
    fling_effect_key: Mapped[Optional[int]] = mapped_column(Integer)
    category_key: Mapped[int] = mapped_column(Integer)
    #baby_trigger_for_key: Mapped[Optional[int]] = mapped_column(Integer)
    #berry_key: Mapped[Optional[int]] = mapped_column(Integer)
    sprite_url: Mapped[Optional[str]] = mapped_column(String(500))

    fling_effect: Mapped["ItemFlingEffect"] = relationship(back_populates="items", cascade="save-update",
                                                           primaryjoin="Item.fling_effect_key == ItemFlingEffect.id",
                                                           foreign_keys=fling_effect_key)
    category: Mapped["ItemCategory"] = relationship(back_populates="items", cascade="save-update",
                                                    primaryjoin="Item.category_key == ItemCategory.id",
                                                    foreign_keys=category_key)
    """ baby_trigger_for: Mapped["EvolutionChain"] = relationship(back_populates="baby_trigger_item",
                                                              primaryjoin="Item.baby_trigger_for_key == EvolutionChain.id",
                                                              foreign_keys=baby_trigger_for_key) """
    baby_trigger_for: Mapped["EvolutionChain"] = relationship(back_populates="baby_trigger_item", cascade="save-update",
                                                              primaryjoin="Item.id == foreign(EvolutionChain.baby_trigger_item_key)")
    
    """ berry: Mapped["Berry"] = relationship(#back_populates="item",
                                          primaryjoin="Item.berry_key == Berry.id",
                                          foreign_keys=berry_key, cascade="save-update") """
    berry: Mapped["Berry"] = relationship(back_populates="item", cascade="save-update",
                                          primaryjoin="Item.id == foreign(Berry.item_key)")

    attributes: Mapped[List["ItemAttribute"]] = relationship(back_populates="items", cascade="save-update",
                                                             secondary=ItemToItemAttributeLink)
    game_indices: Mapped[List["ItemGameIndex"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                               primaryjoin="Item.id == foreign(ItemGameIndex.object_key)")
    held_by_pokemon: Mapped[List["PokemonHeldItem"]] = relationship(back_populates="item", cascade="save-update",
                                            primaryjoin="Item.id == foreign(PokemonHeldItem.item_key)")
    
    machines: Mapped[List["Machine"]] = relationship(back_populates="item", cascade="save-update",
                                                     primaryjoin="Item.id == foreign(Machine.item_key)")
    
    evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="item", cascade="save-update",
                                                                      primaryjoin="Item.id == foreign(EvolutionDetail.item_key)")
    
    held_evolution_details: Mapped[List["EvolutionDetail"]] = relationship(back_populates="held_item", cascade="save-update",
                                                                      primaryjoin="Item.id == foreign(EvolutionDetail.held_item_key)")

    effect_entries: Mapped[List["ItemEffect"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="Item.id == foreign(ItemEffect.object_key)")
    flavor_text_entries: Mapped[List["ItemFlavorText"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="Item.id == foreign(ItemFlavorText.object_key)")
    names: Mapped[List["ItemName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="Item.id == foreign(ItemName.object_key)")
    
    _cache: Dict[int, "Item"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_Item_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "Item":
        poke_api_id = data.id_
        name = data.name
        cost = data.cost
        fling_power = data.fling_power
        sprite_url = data.sprites.default

        item = cls(poke_api_id=poke_api_id, name=name, cost=cost, fling_power=fling_power, sprite_url=sprite_url)
        cls._cache[item.poke_api_id] = item
        return item
    
    def __init__(self, poke_api_id: int, name: str, cost: int, fling_power: int, sprite_url: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name
        self.cost = cost
        self.fling_power = fling_power
        self.sprite_url = sprite_url

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name
        if self.cost != data.cost:
            self.cost = data.cost
        if self.fling_power != data.fling_power:
            self.fling_power = data.fling_power
        if self.sprite_url != data.sprites.default:
            self.sprite_url = data.sprites.default

'''class ItemHolder(Base):
    __tablename__ = "ItemHolder"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    rarity: Mapped[int] = mapped_column(TinyInteger)
    pokemon_key: Mapped[int] = mapped_column(Integer)
    item_key: Mapped[int] = mapped_column(Integer)
    version_key: Mapped[int] = mapped_column(Integer)

    pokemon: Mapped["Pokemon"] = relationship
    item: Mapped["Item"] = relationship
    version: Mapped["Version"] = relationship'''

class ItemAttribute(Base, PokeApiResource):
    __tablename__ = "ItemAttribute"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    items: Mapped[List["Item"]] = relationship(back_populates="attributes", cascade="save-update",
                                               secondary=ItemToItemAttributeLink)
    names: Mapped[List["ItemAttributeName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="ItemAttribute.id == foreign(ItemAttributeName.object_key)")
    descriptions: Mapped[List["ItemAttributeDescription"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="ItemAttribute.id == foreign(ItemAttributeDescription.object_key)")
    
    _cache: Dict[int, "ItemAttribute"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_ItemAttribute_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "ItemAttribute":
        poke_api_id = data.id_
        name = data.name

        att = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[att.poke_api_id] = att
        return att
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name

class ItemCategory(Base, PokeApiResource):
    __tablename__ = "ItemCategory"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    pocket_key: Mapped[int] = mapped_column(Integer)

    pocket: Mapped["ItemPocket"] = relationship(back_populates="categories", cascade="save-update",
                                                primaryjoin="ItemCategory.pocket_key == ItemPocket.id",
                                                foreign_keys=pocket_key)

    items: Mapped[List["Item"]] = relationship(back_populates="category", cascade="save-update",
                                               primaryjoin="ItemCategory.id == foreign(Item.category_key)")
    names: Mapped[List["ItemCategoryName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="ItemCategory.id == foreign(ItemCategoryName.object_key)")
    
    _cache: Dict[int, "ItemCategory"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_ItemCategory_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "ItemCategory":
        poke_api_id = data.id_
        name = data.name

        category = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[category.poke_api_id] = category
        return category
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name

class ItemFlingEffect(Base, PokeApiResource):
    __tablename__ = "ItemFlingEffect"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    items: Mapped[List["Item"]] = relationship(back_populates="fling_effect", cascade="save-update",
                                               primaryjoin="ItemFlingEffect.id == foreign(Item.fling_effect_key)")
    effect_entries: Mapped[List["ItemFlingEffectEffect"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="ItemFlingEffect.id == foreign(ItemFlingEffectEffect.object_key)")
    """ names: Mapped[List["ItemFlingEffectName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="ItemFlingEffect.id == foreign(ItemFlingEffectName.object_key)") """
    _cache: Dict[int, "ItemFlingEffect"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_ItemFlingEffect_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "ItemFlingEffect":
        poke_api_id = data.id_
        name = data.name

        fling_effect = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[fling_effect.poke_api_id] = fling_effect
        return fling_effect
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name

class ItemPocket(Base, PokeApiResource):
    __tablename__ = "ItemPocket"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    categories: Mapped[List["ItemCategory"]] = relationship(back_populates="pocket", cascade="save-update",
                                                            primaryjoin="ItemPocket.id == foreign(ItemCategory.pocket_key)")
    names: Mapped[List["ItemPocketName"]] = relationship(back_populates="object_ref", cascade="save-update",
                                                              primaryjoin="ItemPocket.id == foreign(ItemPocketName.object_key)")
    
    _cache: Dict[int, "ItemPocket"] = {}

    __table_args__ = (
        UniqueConstraint("poke_api_id",name="ux_ItemPocket_PokeApiId"),
    )

    @classmethod
    def parse_data(cls,data) -> "ItemPocket":
        poke_api_id = data.id_
        name = data.name

        pocket = cls(poke_api_id=poke_api_id, name=name)
        cls._cache[pocket.poke_api_id] = pocket
        return pocket
    
    def __init__(self, poke_api_id: int, name: str):
        self.id = get_next_id()
        self.poke_api_id = poke_api_id
        self.name = name

    def compare(self, data):
        if self.name != data.name:
            self.name = data.name