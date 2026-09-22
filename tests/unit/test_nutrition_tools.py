"""Unit test for recipe nutrition calculation tool."""

from app.nutrition_tools import calculate_recipe_nutrition


def test_calculate_recipe_nutrition() -> None:
    result = calculate_recipe_nutrition(
        ingredients=["chicken breast", "spinach", "olive oil"],
        servings=2,
    )
    assert "Nutritional Breakdown (2 servings):" in result
    assert "Total Calories:" in result
    assert "Protein:" in result
    assert "Carbs:" in result
    assert "Fat:" in result
