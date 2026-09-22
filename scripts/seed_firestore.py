#!/usr/bin/env python3
"""Seed script for populating Firestore with sample recipe items."""

import os
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-eb75fbb5d865"
COLLECTION_NAME = "recipes"

SEED_RECIPES = [
    {
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
    {
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
    {
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
    {
        "id": "creamy-garlic-salmon-bowl",
        "title": "Pan-Seared Garlic Salmon Bowl",
        "ingredients": ["salmon fillet", "spinach", "garlic", "olive oil", "lemon"],
        "prep_time_mins": 15,
        "calories": 480,
        "dietary_tags": ["dairy-free", "gluten-free", "nut-free", "keto"],
        "instructions": [
            "Season salmon fillet with salt, pepper, and lemon juice.",
            "Heat olive oil in pan and sear salmon skin-side down for 4 minutes.",
            "Flip salmon, add garlic and spinach, sautéing until tender."
        ],
    },
]


def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    for item in SEED_RECIPES:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"Seeded recipe: {doc_id} ('{item['title']}')")

    print(f"Successfully seeded {len(SEED_RECIPES)} recipes into collection '{COLLECTION_NAME}'!")


if __name__ == "__main__":
    seed()
