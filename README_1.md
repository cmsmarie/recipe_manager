# Recipe Manager

A web-based recipe management system built with Streamlit and PostgreSQL. Designed for college students who want to find recipes based on available ingredients and cooking time.

## What This System Tracks
This system tracks recipes, ingredients, cooking time in minutes, and cuisine type. Users can narrow down what to cook based on the ingredients they have and how much time they have available. It is targeted toward college students who have busy schedules and a limited set of recipes they regularly cook.

## Live App
[Click here to view the live app](https://recipemanager-xjnpyaeuyhcnedounmhz5k.streamlit.app/)

---

## ERD
![ERD](erd.png)

---

## Table Descriptions

**difficulty**
Stores the difficulty levels that can be assigned to a recipe.
- id: unique identifier
- level: difficulty label (Easy, Medium, Hard)

**recipes**
Stores all recipe information.
- id: unique identifier
- recipe_name: name of the recipe
- description: optional description of the recipe
- cuisine: type of cuisine (e.g. American, Asian)
- cook_time_minutes: how long the recipe takes to prep and cook
- difficulty_id: references the difficulty table

**ingredients**
Stores all ingredients that can be linked to recipes.
- id: unique identifier
- name: name of the ingredient
- category: category of the ingredient (e.g. Dairy, Protein, Vegetable)

**recipe_ingredients**
Junction table linking recipes to ingredients.
- id: unique identifier
- recipe_id: references the recipes table
- ingredient_id: references the ingredients table
- quantity: how much of the ingredient is needed (e.g. 2 cups)
- linked_at: timestamp of when the ingredient was linked to the recipe

---

## How to Run Locally

1. Clone the repository:
   git clone https://github.com/your-username/your-repo-name.git

2. Install dependencies:
   pip install streamlit psycopg2-binary

3. Create a secrets file at .streamlit/secrets.toml and add your database URL:
   DB_URL = "postgresql://username:password@host:port/dbname"

4. Run the app:
   streamlit run Project_1/project1_app.py
