# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.items_api_base import BaseItemsApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import StrictInt
from typing import Any, List
from openapi_server.models.item import Item


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/items",
    responses={
        201: {"description": "Shopping item added successfully"},
    },
    tags=["Items"],
    summary="Add a new shopping list item",
    response_model_by_alias=True,
)
async def add_item(
    item: Item = Body(None, description=""),
) -> None:
    if not BaseItemsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseItemsApi.subclasses[0]().add_item(item)


@router.delete(
    "/items/{item_id}",
    responses={
        204: {"description": "Item deleted successfully"},
        404: {"description": "Item not found"},
    },
    tags=["Items"],
    summary="Delete a shopping list item",
    response_model_by_alias=True,
)
async def delete_item(
    item_id: StrictInt = Path(..., description=""),
) -> None:
    if not BaseItemsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseItemsApi.subclasses[0]().delete_item(item_id)


@router.get(
    "/items/{item_id}",
    responses={
        200: {"model": Item, "description": "Details of the shopping item"},
        404: {"description": "Item not found"},
    },
    tags=["Items"],
    summary="Get details of a specific shopping item",
    response_model_by_alias=True,
)
async def get_item_by_id(
    item_id: StrictInt = Path(..., description=""),
) -> Item:
    if not BaseItemsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseItemsApi.subclasses[0]().get_item_by_id(item_id)


@router.get(
    "/items",
    responses={
        200: {"model": List[Item], "description": "A list of shopping items"},
    },
    tags=["Items"],
    summary="Get a list of all shopping list items",
    response_model_by_alias=True,
)
async def get_items(
) -> List[Item]:
    if not BaseItemsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseItemsApi.subclasses[0]().get_items()


@router.put(
    "/items/{item_id}",
    responses={
        200: {"description": "Shopping item updated successfully"},
        404: {"description": "Item not found"},
    },
    tags=["Items"],
    summary="Update a shopping list item",
    response_model_by_alias=True,
)
async def update_item(
    item_id: StrictInt = Path(..., description=""),
    item: Item = Body(None, description=""),
) -> None:
    if not BaseItemsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseItemsApi.subclasses[0]().update_item(item_id, item)
