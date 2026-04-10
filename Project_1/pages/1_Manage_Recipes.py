import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Recipes", page_icon="📋")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📋 Manage Recipes")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, level FROM difficulty ORDER BY id;")
    difficulty_rows = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error("Error loading difficulty levels: " + str(e))
    st.stop()

difficulty_options = {row[1]: row[0] for row in difficulty_rows}
difficulty_levels = list(difficulty_options.keys())

st.subheader("Add a New Recipe")
with st.form("add_recipe_form"):
    recipe_name = st.text_input("Recipe Name *")
    description = st.text_area("Description")
    cuisine = st.text_input("Cuisine *")
    cook_time = st.number_input("Cook Time (minutes) *", min_value=1, step=1)
    difficulty = st.selectbox("Difficulty *", difficulty_levels)
    submitted = st.form_submit_button("Add Recipe")

    if submitted:
        errors = []
        if not recipe_name.strip():
            errors.append("Recipe Name is required.")
        if not cuisine.strip():
            errors.append("Cuisine is required.")
        if cook_time < 1:
            errors.append("Cook Time must be a positive number.")
        if errors:
            for err in errors:
                st.error(err)
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO recipes (recipe_name, description, cuisine, cook_time_minutes, difficulty_id) VALUES (%s, %s, %s, %s, %s);",
                    (recipe_name.strip(), description.strip(), cuisine.strip(), cook_time, difficulty_options[difficulty])
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success("Recipe " + recipe_name + " added successfully!")
            except Exception as e:
                st.error("Error: " + str(e))

st.markdown("---")
st.subheader("Current Recipes")
search = st.text_input("Search recipes by name or cuisine")

try:
    conn = get_connection()
    cur = conn.cursor()
    if search.strip():
        cur.execute(
            "SELECT r.id, r.recipe_name, r.cuisine, r.cook_time_minutes, d.level, r.description FROM recipes r JOIN difficulty d ON r.difficulty_id = d.id WHERE r.recipe_name ILIKE %s OR r.cuisine ILIKE %s ORDER BY r.recipe_name;",
            ("%" + search.strip() + "%", "%" + search.strip() + "%")
        )
    else:
        cur.execute(
            "SELECT r.id, r.recipe_name, r.cuisine, r.cook_time_minutes, d.level, r.description FROM recipes r JOIN difficulty d ON r.difficulty_id = d.id ORDER BY r.recipe_name;"
        )
    recipes = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error("Error: " + str(e))
    st.stop()

if not recipes:
    st.info("No recipes found.")
else:
    for r in recipes:
        rid = r[0]
        rname = r[1]
        rcuisine = r[2]
        rcook = r[3]
        rdiff = r[4]
        rdesc = r[5]
        with st.expander(rname + " — " + rcuisine + " | " + str(rcook) + " min | " + rdiff):
            with st.form("edit_recipe_" + str(rid)):
                new_name = st.text_input("Recipe Name *", value=rname)
                new_desc = st.text_area("Description", value=rdesc or "")
                new_cuisine = st.text_input("Cuisine *", value=rcuisine)
                new_cook = st.number_input("Cook Time (minutes) *", min_value=1, step=1, value=rcook)
                current_index = difficulty_levels.index(rdiff) if rdiff in difficulty_levels else 0
                new_diff = st.selectbox("Difficulty *", difficulty_levels, index=current_index)
                update = st.form_submit_button("Save Changes")

                if update:
                    errors = []
                    if not new_name.strip():
                        errors.append("Recipe Name is required.")
                    if not new_cuisine.strip():
                        errors.append("Cuisine is required.")
                    if new_cook < 1:
                        errors.append("Cook Time must be a positive number.")
                    if errors:
                        for err in errors:
                            st.error(err)
                    else:
