# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.external_recipe_tools import search_online_recipes
from app.firestore_tools import add_recipe, get_recipe, search_recipes
from app.image_tools import generate_dish_image
from app.video_tools import generate_dish_video
from app.nutrition_tools import calculate_recipe_nutrition
from app.rag_tools import consult_herbal_corpus



def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


REASONING_ENGINE_ID = "projects/435158051870/locations/us-central1/reasoningEngines/7589519198456381440"

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=REASONING_ENGINE_ID
)


async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        pass
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Smart Pantry Chef, a dedicated culinary assistant with strict attention to dietary safety. "
        "CRITICAL MEMORY MANDATE: Always record and remember all user food allergies (e.g. dairy, peanuts, tree nuts, shellfish, gluten, eggs, soy), "
        "intolerances, dietary restrictions, and pantry inventory across all sessions. "
        "When recommending recipes or cooking advice, NEVER suggest ingredients that contain any of the user's recorded allergies or restrictions."
    ),
    workflow_description=(
        "Analyze the request and return structured UI when appropriate. "
        "Use the Firestore tools (search_recipes, get_recipe, add_recipe) to search for, inspect, or add recipes to your catalog. "
        "Use search_online_recipes to search for live external recipes and inspiration from public recipe databases. "
        "Use calculate_recipe_nutrition to compute calories, protein, carbs, and fat breakdown for recipes. "
        "Use generate_dish_image to render high-quality presentation artwork or photos of dishes and recipes. "
        "Use consult_herbal_corpus to answer questions about traditional botanical remedies, plant uses, and herbal culinary history. "
        "You also have a secure Python sandbox code execution capability. Use Python code execution for complex math, data manipulation, unit conversions, or precise nutritional analysis."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        get_weather,
        get_current_time,
        search_recipes,
        get_recipe,
        add_recipe,
        search_online_recipes,
        calculate_recipe_nutrition,
        generate_dish_image,
        generate_dish_video,
        consult_herbal_corpus,
        PreloadMemoryTool(),
    ],
    code_executor=code_executor,
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
