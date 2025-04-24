# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictInt
from typing import Any, List
from openapi_server.models.item import Item


class BaseItemsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseItemsApi.subclasses = BaseItemsApi.subclasses + (cls,)
    async def add_item(
        self,
        item: Item,
    ) -> None:
        ...


    async def delete_item(
        self,
        item_id: StrictInt,
    ) -> None:
        ...


    async def get_item_by_id(
        self,
        item_id: StrictInt,
    ) -> Item:
        ...


    async def get_items(
        self,
    ) -> List[Item]:
        ...


    async def update_item(
        self,
        item_id: StrictInt,
        item: Item,
    ) -> None:
        ...
