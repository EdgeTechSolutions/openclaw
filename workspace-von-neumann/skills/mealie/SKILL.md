---
name: mealie
description: >
  Manage recipes, shopping lists, meal plans, and food database via the Mealie
  self-hosted recipe manager API. Supports searching recipes, importing from URLs,
  planning weekly meals, building shopping lists, and managing the ingredient database.
baseUrl: https://hrana.stopar.si
requiresEnv:
  - MEALIE_TOKEN
optionalEnv:
  - MEALIE_URL
scripts:
  - {baseDir}/scripts/recipes.py
  - {baseDir}/scripts/shopping.py
  - {baseDir}/scripts/mealplan.py
  - {baseDir}/scripts/foods.py
---

# Mealie Skill

Interact with your [Mealie](https://mealie.io/) self-hosted recipe manager at **https://hrana.stopar.si**.

## Setup

```bash
export MEALIE_URL=https://hrana.stopar.si   # (optional, this is the default)
export MEALIE_TOKEN=your_api_token_here
```

Get your API token from **Mealie → User Settings → API Tokens**.

All scripts also accept `--url` and `--token` flags for one-off use.

---

## recipes.py — Recipe Management

Manage your recipe library: list, search, view, import, create, and delete recipes.

### List recipes

```bash
# List all recipes (default 20 per page)
python3 {baseDir}/scripts/recipes.py list

# Search for pasta recipes
python3 {baseDir}/scripts/recipes.py list --search pasta

# Filter by category
python3 {baseDir}/scripts/recipes.py list --category "Italian"

# Filter by tag
python3 {baseDir}/scripts/recipes.py list --tag "quick"

# Paginate results
python3 {baseDir}/scripts/recipes.py list --limit 50 --page 2
```

### View a recipe

```bash
# Get full recipe details by slug (slug is shown in list output)
python3 {baseDir}/scripts/recipes.py get --slug spaghetti-bolognese
```

Output includes: name, description, rating, categories, tags, ingredients (with quantities), step-by-step instructions, nutrition info, and source URL.

### Import a recipe from a URL

```bash
# Mealie scrapes the recipe automatically
python3 {baseDir}/scripts/recipes.py create-url --url-source "https://www.allrecipes.com/recipe/213742/cheesy-chicken-broccoli-casserole/"
```

### Create a recipe from JSON

```bash
# From a JSON file
python3 {baseDir}/scripts/recipes.py create --file my_recipe.json

# From stdin
echo '{"name": "Simple Salad"}' | python3 {baseDir}/scripts/recipes.py create
```

### Delete a recipe

```bash
python3 {baseDir}/scripts/recipes.py delete --slug old-recipe-slug
# Will prompt for confirmation
```

---

## shopping.py — Shopping List Management

Manage shopping lists: view, create, add items, check off items, and sync with recipes.

### List all shopping lists

```bash
python3 {baseDir}/scripts/shopping.py lists
```

### View a shopping list

```bash
# Shows items grouped by section/label with check status
python3 {baseDir}/scripts/shopping.py get --list-id <list-uuid>
```

Output shows:
- ✅ for checked (purchased) items
- ⬜ for unchecked (still needed) items
- Items grouped by label/aisle if configured
- Item IDs for further operations

### Create a new shopping list

```bash
python3 {baseDir}/scripts/shopping.py create-list --name "Weekend Shopping"
```

### Add items to a list

```bash
# Add a freeform item
python3 {baseDir}/scripts/shopping.py add --list-id <list-uuid> --note "Parmesan cheese"

# Add with quantity (format: "qty unit name")
python3 {baseDir}/scripts/shopping.py add --list-id <list-uuid> --item "2 cups flour"

# Add multiple items at once
python3 {baseDir}/scripts/shopping.py add --list-id <list-uuid> \
  --item "500 g ground beef" \
  --item "1 can tomatoes" \
  --item "200 g spaghetti"
```

### Check/uncheck an item

```bash
# Mark as purchased
python3 {baseDir}/scripts/shopping.py check --item-id <item-uuid> --checked true

# Mark as not purchased
python3 {baseDir}/scripts/shopping.py check --item-id <item-uuid> --checked false
```

### Remove an item

```bash
python3 {baseDir}/scripts/shopping.py remove --item-id <item-uuid>
```

### Clear all checked items

```bash
# Clean up your list after shopping
python3 {baseDir}/scripts/shopping.py clear-checked --list-id <list-uuid>
```

### Add recipe ingredients to a list

```bash
# Adds all ingredients from a recipe directly to your shopping list
python3 {baseDir}/scripts/shopping.py add-recipe --list-id <list-uuid> --recipe-id <recipe-uuid>
```

---

## mealplan.py — Meal Plan Management

Plan your meals by day, view today's plan, and get random suggestions.

### View today's meal plan

```bash
python3 {baseDir}/scripts/mealplan.py today
```

### List meal plans for a date range

```bash
# This week
python3 {baseDir}/scripts/mealplan.py list --start-date 2026-03-02 --end-date 2026-03-08

# Just today
python3 {baseDir}/scripts/mealplan.py list --start-date 2026-03-01 --end-date 2026-03-01
```

### Add a recipe to the meal plan

```bash
# Add dinner for today
python3 {baseDir}/scripts/mealplan.py add --recipe-slug spaghetti-bolognese --entry-type dinner

# Add lunch for a specific date
python3 {baseDir}/scripts/mealplan.py add \
  --date 2026-03-05 \
  --entry-type lunch \
  --recipe-slug caesar-salad

# Add breakfast
python3 {baseDir}/scripts/mealplan.py add --date 2026-03-03 --entry-type breakfast --recipe-slug overnight-oats
```

### Add a note (without a recipe)

```bash
# Plan a restaurant meal or note
python3 {baseDir}/scripts/mealplan.py add \
  --date 2026-03-07 \
  --entry-type dinner \
  --title "Date Night" \
  --text "Reservations at La Maison, 7pm"
```

### Get a random recipe suggestion

```bash
# Random dinner suggestion for today
python3 {baseDir}/scripts/mealplan.py random --entry-type dinner

# Random lunch for next Friday
python3 {baseDir}/scripts/mealplan.py random --date 2026-03-06 --entry-type lunch
```

### Delete a meal plan entry

```bash
python3 {baseDir}/scripts/mealplan.py delete --plan-id <plan-uuid>
```

---

## foods.py — Food/Ingredient Database

Manage the food/ingredient database used for structured recipe ingredients and shopping.

### List foods

```bash
# List all foods (up to 50)
python3 {baseDir}/scripts/foods.py list

# Search for a specific food
python3 {baseDir}/scripts/foods.py list --search "tomato"

# Show more results
python3 {baseDir}/scripts/foods.py list --limit 200
```

### Create a food

```bash
python3 {baseDir}/scripts/foods.py create --name "Haloumi cheese"
```

### Delete a food

```bash
python3 {baseDir}/scripts/foods.py delete --food-id <food-uuid>
# Will prompt for confirmation
```

---

## 🔄 Complete Workflow: Recipe → Meal Plan → Shopping List

Here's a full workflow for planning a week of meals and building a shopping list:

### Step 1: Find and explore recipes

```bash
# Search for recipe ideas
python3 {baseDir}/scripts/recipes.py list --search "chicken"

# Inspect a recipe in detail
python3 {baseDir}/scripts/recipes.py get --slug lemon-herb-chicken
```

### Step 2: Import a new recipe

```bash
# Import from a cooking website
python3 {baseDir}/scripts/recipes.py create-url \
  --url-source "https://www.seriouseats.com/the-best-roast-chicken"
# Note the slug from the output
```

### Step 3: Plan meals for the week

```bash
# Monday
python3 {baseDir}/scripts/mealplan.py add --date 2026-03-02 --entry-type dinner --recipe-slug lemon-herb-chicken
python3 {baseDir}/scripts/mealplan.py add --date 2026-03-02 --entry-type lunch --recipe-slug caesar-salad

# Tuesday  
python3 {baseDir}/scripts/mealplan.py add --date 2026-03-03 --entry-type dinner --recipe-slug spaghetti-bolognese

# Get random suggestion for Wednesday
python3 {baseDir}/scripts/mealplan.py random --date 2026-03-04 --entry-type dinner

# Review the week
python3 {baseDir}/scripts/mealplan.py list --start-date 2026-03-02 --end-date 2026-03-08
```

### Step 4: Create a shopping list

```bash
# Create a new list for the week
python3 {baseDir}/scripts/shopping.py create-list --name "Week of March 2"
# Note the list ID from the output: <list-uuid>
```

### Step 5: Add recipe ingredients to the shopping list

```bash
# Get recipe IDs from the recipe details
python3 {baseDir}/scripts/recipes.py get --slug lemon-herb-chicken
# Then add ingredients to shopping list
python3 {baseDir}/scripts/shopping.py add-recipe --list-id <list-uuid> --recipe-id <recipe-uuid>

python3 {baseDir}/scripts/shopping.py add-recipe --list-id <list-uuid> --recipe-id <spaghetti-recipe-uuid>

# Add any extra items manually
python3 {baseDir}/scripts/shopping.py add --list-id <list-uuid> --note "Olive oil"
python3 {baseDir}/scripts/shopping.py add --list-id <list-uuid> --item "2 bottles wine"
```

### Step 6: Shop and check off items

```bash
# View the list while shopping
python3 {baseDir}/scripts/shopping.py get --list-id <list-uuid>

# Check off items as you find them
python3 {baseDir}/scripts/shopping.py check --item-id <item-uuid> --checked true

# After shopping, clear checked items
python3 {baseDir}/scripts/shopping.py clear-checked --list-id <list-uuid>
```

### Step 7: Check today's plan before cooking

```bash
python3 {baseDir}/scripts/mealplan.py today
```

---

## Tips

- **Slugs**: Recipe slugs are URL-friendly names (e.g., `spaghetti-bolognese`). They appear in recipe URLs and list output.
- **IDs**: UUIDs are used for shopping lists, items, foods, and meal plan entries. Always copy them from command output.
- **Pagination**: For large recipe libraries, use `--page` and `--limit` to browse through results.
- **Token**: Generate your API token in Mealie under **User Settings → API Tokens**. Store it in `MEALIE_TOKEN`.
- **perPage=-1**: The scripts use `perPage=-1` when fetching all items (e.g., shopping lists) to avoid pagination.
