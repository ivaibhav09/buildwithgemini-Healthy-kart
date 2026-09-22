"""Unit tests for Firestore recipe tools."""

from app.firestore_tools import add_recipe, get_recipe, search_recipes


def test_search_recipes() -> None:
    results = search_recipes(ingredient="spinach")
    assert "Spinach" in results or "spinach" in results


def test_get_recipe() -> None:
    details = get_recipe("garlic-spinach-chicken")
    assert "Garlic Spinach Chicken Skillet" in details
    assert "Ingredients:" in details


def test_add_recipe() -> None:
    response = add_recipe(
        title="Quick Garlic Toast",
        ingredients=["bread", "garlic", "olive oil"],
        prep_time_mins=5,
        calories=150,
        dietary_tags=["vegan", "dairy-free"],
        instructions=["Toast bread", "Rub with garlic and olive oil"],
    )
    assert "created" in response
    assert "quick-garlic-toast" in response
