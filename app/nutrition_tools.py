"""Minimal nutrition calculation tool for recipe ingredients."""

from typing import Any

# Standard macro lookup database (per standard portion)
_NUTRITION_DATABASE: dict[str, dict[str, float]] = {
    "chicken breast": {"calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6},
    "chicken": {"calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6},
    "salmon": {"calories": 206, "protein": 22.0, "carbs": 0.0, "fat": 12.0},
    "eggs": {"calories": 140, "protein": 12.0, "carbs": 1.0, "fat": 10.0},
    "egg": {"calories": 70, "protein": 6.0, "carbs": 0.5, "fat": 5.0},
    "spinach": {"calories": 25, "protein": 3.0, "carbs": 3.5, "fat": 0.4},
    "garlic": {"calories": 15, "protein": 0.6, "carbs": 3.3, "fat": 0.1},
    "olive oil": {"calories": 120, "protein": 0.0, "carbs": 0.0, "fat": 14.0},
    "lemon juice": {"calories": 10, "protein": 0.1, "carbs": 3.0, "fat": 0.0},
    "rice": {"calories": 205, "protein": 4.2, "carbs": 45.0, "fat": 0.4},
    "bread": {"calories": 160, "protein": 6.0, "carbs": 28.0, "fat": 2.0},
    "cheese": {"calories": 110, "protein": 7.0, "carbs": 1.0, "fat": 9.0},
}


def calculate_recipe_nutrition(ingredients: list[str], servings: int = 1) -> str:
    """Calculates estimated total calories, macronutrients (protein, carbs, fat),
    and per-serving nutritional breakdown for a list of recipe ingredients.

    Args:
        ingredients: List of ingredient names (e.g. ['chicken breast', 'spinach', 'olive oil']).
        servings: Number of servings to scale by (default is 1).

    Returns:
        Formatted string summarizing total calories, protein (g), carbs (g), and fat (g).
    """
    servings = max(1, servings)
    total_cal = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    breakdown_items = []

    for ing in ingredients:
        ing_clean = ing.lower().strip()
        matched_info = None

        for key, info in _NUTRITION_DATABASE.items():
            if key in ing_clean:
                matched_info = info
                break

        if not matched_info:
            # Fallback estimation for unknown ingredients
            matched_info = {"calories": 50.0, "protein": 2.0, "carbs": 5.0, "fat": 1.0}

        cal = matched_info["calories"]
        p = matched_info["protein"]
        c = matched_info["carbs"]
        f = matched_info["fat"]

        total_cal += cal
        total_protein += p
        total_carbs += c
        total_fat += f
        breakdown_items.append(f"- {ing}: ~{int(cal)} kcal | P: {p}g | C: {c}g | F: {f}g")

    per_serving_cal = int(total_cal / servings)
    per_serving_p = round(total_protein / servings, 1)
    per_serving_c = round(total_carbs / servings, 1)
    per_serving_f = round(total_fat / servings, 1)

    return (
        f"Nutritional Breakdown ({servings} serving{'s' if servings > 1 else ''}):\n"
        f"Total Calories: {int(total_cal)} kcal ({per_serving_cal} kcal/serving)\n"
        f"Protein: {round(total_protein, 1)}g ({per_serving_p}g/serving)\n"
        f"Carbs: {round(total_carbs, 1)}g ({per_serving_c}g/serving)\n"
        f"Fat: {round(total_fat, 1)}g ({per_serving_f}g/serving)\n\n"
        f"Ingredient Breakdown:\n" + "\n".join(breakdown_items)
    )
