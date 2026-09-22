"""Function tool to search online recipes via free public API (TheMealDB)."""

import os
import urllib.parse
import urllib.request
import json
import logging

logger = logging.getLogger(__name__)

# Reads API key from environment variable if provided, defaulting to free public key '1'
THEMEALDB_API_KEY = os.getenv("THEMEALDB_API_KEY", "1")
BASE_URL = f"https://www.themealdb.com/api/json/v1/{THEMEALDB_API_KEY}"


def _fetch_meals(search_term: str) -> list[dict]:
    encoded_query = urllib.parse.quote(search_term.strip())
    url = f"{BASE_URL}/search.php?s={encoded_query}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SmartPantryChef/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("meals") or []
    except Exception as e:
        logger.error("Error fetching from TheMealDB for '%s': %s", search_term, e)
    return []


def search_online_recipes(query: str) -> str:
    """Search for real recipes online using TheMealDB public API.

    Args:
        query: Recipe or main ingredient search term (e.g. 'chicken', 'pasta', 'arrabiata').

    Returns:
        Formatted summary of online recipes including title, cuisine area, category, ingredients, and instructions.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        return "Please provide a query term to search online recipes."

    meals = _fetch_meals(cleaned_query)

    # Fallback to individual key terms if multi-word query returned no direct hits
    if not meals and " " in cleaned_query:
        for word in cleaned_query.split():
            if len(word) > 3:
                meals = _fetch_meals(word)
                if meals:
                    break

    if not meals:
        return f"No online recipes found matching query '{query}'."

    summaries = []
    for meal in meals[:3]:  # Top 3 matching recipes
        title = meal.get("strMeal", "Unknown Dish")
        category = meal.get("strCategory", "General")
        area = meal.get("strArea", "International")
        instructions = meal.get("strInstructions", "No instructions provided.").replace("\r\n", "\n")

        # Collect up to 20 ingredients & measures
        ingredients = []
        for i in range(1, 21):
            ing = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ing and ing.strip():
                measure_str = f" ({measure.strip()})" if measure and measure.strip() else ""
                ingredients.append(f"{ing.strip()}{measure_str}")

        summaries.append(
            f"🍽️ **{title}** ({area} {category})\n"
            f"Ingredients: {', '.join(ingredients)}\n"
            f"Instructions:\n{instructions[:300]}..."
        )

    return "\n\n---\n\n".join(summaries)
