import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Recipes", page_icon="📋")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📋 Manage Recipes")

with st.form("add_recipe_form"):
    recipe_name = st.text_input("Recipe Name")
    description = st.text_area("Description")
    cuisine = st.text_input("Cuisine")
    cook_time = st.number_input("Cook Time (minutes)", min_value=1, step=1)
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    submitted = st.form_submit_button("Add Recipe")

    if submitted:
        if recipe_name and cuisine and difficulty:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO recipes (recipe_name, description, cuisine, cook_time_minutes, difficulty)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (recipe_name, description, cuisine, cook_time, difficulty)
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ Recipe '{recipe_name}' added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please fill in all required fields.")

st.markdown("---")
st.subheader("Current Recipes")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, recipe_name, cuisine, cook_time_minutes, difficulty FROM recipes ORDER BY recipe_name;")
    recipes = cur.fetchall()
    cur.close()
    conn.close()

    if recipes:
        st.table([
            {"ID": r[0], "Recipe": r[1], "Cuisine": r[2], "Cook Time (min)": r[3], "Difficulty": r[4]}
            for r in recipes
        ])
    else:
        st.info("No recipes yet.")
except Exception as e:
    st.error(f"Error: {e}")
