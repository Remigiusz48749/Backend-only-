# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictInt  # noqa: F401
from typing import Any, List  # noqa: F401
from openapi_server.models.item import Item  # noqa: F401


def test_add_item(client: TestClient):
    """Test case for add_item

    Add a new shopping list item
    """
    item = {"note":"Whole grain","quantity":2,"name":"Bread","id":1}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/items",
    #    headers=headers,
    #    json=item,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_item(client: TestClient):
    """Test case for delete_item

    Delete a shopping list item
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/items/{item_id}".format(item_id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_item_by_id(client: TestClient):
    """Test case for get_item_by_id

    Get details of a specific shopping item
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/items/{item_id}".format(item_id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_items(client: TestClient):
    """Test case for get_items

    Get a list of all shopping list items
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/items",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_update_item(client: TestClient):
    """Test case for update_item

    Update a shopping list item
    """
    item = {"note":"Whole grain","quantity":2,"name":"Bread","id":1}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/items/{item_id}".format(item_id=56),
    #    headers=headers,
    #    json=item,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

