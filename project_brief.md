# My agent: smart-pantry-chef
One-liner: A conversational agent that helps home cooks create meals from their pantry ingredients with a catalog of recipes.

Tool coverage:
- Memory: Tracks pantry inventory, dietary restrictions, and cooking preferences
- Tools: Queries recipe database and computes nutritional breakdown
- Catalog/UI: Renders step-by-step recipe cards and ingredient tables (A2UI)
- Image gen: Generates dish presentation artwork
- Sandbox: Calculates calorie totals, macro ratios, and portion scaling

Core rails (everyone): memory, tools, eval, deploy, frontend
My stretch menu (pick later): A2UI recipe cards, image generation, nutritional code sandbox calculation
First eval question: "What dinner can I make with chicken, garlic, and spinach given my dairy-free restriction?"
