"""Firestore tools for reading and writing recipes in the Firestore database."""

import logging
from typing import Any
from google.cloud import firestore
from google.api_core.exceptions import NotFound

logger = logging.getLogger(__name__)

# Hardcoded project ID as required for Agent Platform deployment safety
PROJECT_ID = "qwiklabs-gcp-01-eb75fbb5d865"
COLLECTION_NAME = "recipes"

# In-memory fallback dataset in case Cloud Firestore (default) database has not yet been initialized in GCP Console
_FALLBACK_RECIPES: dict[str, dict[str, Any]] = {
    "garlic-spinach-chicken": {
        "id": "garlic-spinach-chicken",
        "title": "Garlic Spinach Chicken Skillet",
        "ingredients": ["chicken breast", "spinach", "garlic", "olive oil", "salt", "black pepper"],
        "prep_time_mins": 20,
        "calories": 380,
        "dietary_tags": ["dairy-free", "gluten-free", "nut-free", "high-protein"],
        "instructions": [
            "Season chicken breast with salt and pepper.",
            "Heat olive oil in a skillet over medium-high heat.",
            "Sauté minced garlic for 1 minute until fragrant.",
            "Add chicken breast slices and cook for 6-8 minutes until golden.",
            "Toss in fresh spinach and cook until wilted. Serve hot."
        ],
    },
    "spinach-garlic-egg-scramble": {
        "id": "spinach-garlic-egg-scramble",
        "title": "Garlic & Spinach Egg Scramble",
        "ingredients": ["eggs", "spinach", "garlic", "olive oil", "black pepper"],
        "prep_time_mins": 10,
        "calories": 250,
        "dietary_tags": ["dairy-free", "gluten-free", "nut-free", "vegetarian"],
        "instructions": [
            "Whisk eggs in a small bowl.",
            "Heat olive oil in a non-stick pan over medium heat.",
            "Add minced garlic and spinach, cooking until spinach wilts.",
            "Pour in whisked eggs and gently scramble until cooked to your liking."
        ],
    },
    "lemon-herb-grilled-chicken": {
        "id": "lemon-herb-grilled-chicken",
        "title": "Lemon Herb Grilled Chicken",
        "ingredients": ["chicken breast", "lemon juice", "olive oil", "oregano", "garlic"],
        "prep_time_mins": 25,
        "calories": 410,
        "dietary_tags": ["dairy-free", "gluten-free", "nut-free", "paleo"],
        "instructions": [
            "Marinate chicken breast in lemon juice, olive oil, oregano, and minced garlic for 15 mins.",
            "Preheat grill or grill pan to medium-high.",
            "Grill chicken for 6-7 minutes per side until internal temperature reaches 165°F."
        ],
    },
}


def _get_db():
    return firestore.Client(project=PROJECT_ID)


def search_recipes(ingredient: str = "", dietary_tag: str = "") -> str:
    """Search for recipes in the Firestore database matching an ingredient or dietary tag.

    Args:
        ingredient: Optional ingredient to filter by (e.g. 'spinach', 'chicken').
        dietary_tag: Optional dietary tag to filter by (e.g. 'dairy-free', 'gluten-free').

    Returns:
        Formatted string listing matching recipes and their ingredients/details.
    """
    try:
        db = _get_db()
        col_ref = db.collection(COLLECTION_NAME)
        docs = list(col_ref.stream())
        results = [d.to_dict() for d in docs]
    except NotFound:
        logger.warning("Firestore database (default) not found, using fallback dataset.")
        results = list(_FALLBACK_RECIPES.values())
    except Exception as e:
        logger.warning("Firestore read error (%s), using fallback dataset.", e)
        results = list(_FALLBACK_RECIPES.values())

    matched = []
    for recipe in results:
        ing_list = [i.lower() for i in recipe.get("ingredients", [])]
        tags_list = [t.lower() for t in recipe.get("dietary_tags", [])]

        match_ing = not ingredient or any(ingredient.lower() in item for item in ing_list)
        match_tag = not dietary_tag or any(dietary_tag.lower() in tag for tag in tags_list)

        if match_ing and match_tag:
            matched.append(recipe)

    if not matched:
        return f"No recipes found matching ingredient='{ingredient}', dietary_tag='{dietary_tag}'."

    summary_lines = []
    for r in matched:
        summary_lines.append(
            f"- [{r.get('id')}] {r.get('title')} ({r.get('prep_time_mins', 0)} mins, {r.get('calories', 0)} kcal)\n"
            f"  Ingredients: {', '.join(r.get('ingredients', []))}\n"
            f"  Dietary Tags: {', '.join(r.get('dietary_tags', []))}"
        )
    return "\n\n".join(summary_lines)


def get_recipe(recipe_id: str) -> str:
    """Fetch complete details and cooking instructions for a specific recipe ID from Firestore.

    Args:
        recipe_id: The unique ID/slug of the recipe (e.g. 'garlic-spinach-chicken').

    Returns:
        Formatted string containing ingredients, prep time, calories, and instructions.
    """
    recipe = None
    try:
        db = _get_db()
        doc_ref = db.collection(COLLECTION_NAME).document(recipe_id)
        doc = doc_ref.get()
        if doc.exists:
            recipe = doc.to_dict()
    except NotFound:
        logger.warning("Firestore database (default) not found, using fallback dataset.")
        recipe = _FALLBACK_RECIPES.get(recipe_id)
    except Exception as e:
        logger.warning("Firestore get_recipe error (%s), using fallback dataset.", e)
        recipe = _FALLBACK_RECIPES.get(recipe_id)

    if not recipe:
        return f"Recipe '{recipe_id}' not found."

    instructions_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(recipe.get("instructions", [])))
    return (
        f"Title: {recipe.get('title')}\n"
        f"Prep Time: {recipe.get('prep_time_mins')} minutes | Calories: {recipe.get('calories')} kcal\n"
        f"Dietary Tags: {', '.join(recipe.get('dietary_tags', []))}\n"
        f"Ingredients: {', '.join(recipe.get('ingredients', []))}\n\n"
        f"Instructions:\n{instructions_str}"
    )


def add_recipe(
    title: str,
    ingredients: list[str],
    prep_time_mins: int = 15,
    calories: int = 350,
    dietary_tags: list[str] | None = None,
    instructions: list[str] | None = None,
) -> str:
    """Add a new recipe document into the Firestore 'recipes' collection.

    Args:
        title: Title of the recipe (e.g. 'Chicken Garlic Stir-Fry').
        ingredients: List of ingredient strings.
        prep_time_mins: Preparation time in minutes.
        calories: Estimated calories per serving.
        dietary_tags: List of dietary tags (e.g. ['dairy-free', 'gluten-free']).
        instructions: Step-by-step cooking instructions list.

    Returns:
        Confirmation message with the created recipe ID.
    """
    dietary_tags = dietary_tags or []
    instructions = instructions or []
    recipe_id = title.lower().replace(" ", "-").replace("&", "and")

    data = {
        "id": recipe_id,
        "title": title,
        "ingredients": ingredients,
        "prep_time_mins": prep_time_mins,
        "calories": calories,
        "dietary_tags": dietary_tags,
        "instructions": instructions,
    }

    try:
        db = _get_db()
        db.collection(COLLECTION_NAME).document(recipe_id).set(data)
        status = "Saved successfully to Firestore!"
    except NotFound:
        logger.warning("Firestore database (default) not found, saved to in-memory fallback.")
        _FALLBACK_RECIPES[recipe_id] = data
        status = "Saved to local fallback memory (Firestore default DB needs creation in console)."
    except Exception as e:
        logger.warning("Firestore write error (%s), saved to fallback.", e)
        _FALLBACK_RECIPES[recipe_id] = data
        status = f"Saved to local fallback memory (Firestore error: {e})."

    return f"Recipe '{title}' (ID: {recipe_id}) created. {status}"
