"""Unit test for online recipe search tool."""

from app.external_recipe_tools import search_online_recipes


def test_search_online_recipes() -> None:
    result = search_online_recipes("arrabiata")
    assert "Arrabiata" in result or "Penne" in result or "Ingredients:" in result
