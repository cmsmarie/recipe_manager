import streamlit as st
import psycopg2

st.set_page_config(page_title="Recipe Manager", page_icon="🍽️")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🍽️ Recipe Manager")
st.write("Welcome! Use the sidebar to manage recipes and ingredients.")

st.markdown("---")
st.subheader("📊 Current Data")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM recipes;")
    recipe_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM ingredients;")
    ingredient_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM recipe_ingredients;")
    link_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM difficulty;")
    difficulty_count = cur.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🍲 Recipes", recipe_count)
    col2.metric("🥕 Ingredients", ingredient_count)
    col3.metric("🔗 Links", link_count)
    col4.metric("⚡ Difficulty Levels", difficulty_count)

    st.markdown("---")
    st.subheader("📋 All Recipes & Ingredients")
    cur.execute("""
        SELECT r.recipe_name, r.cuisine, r.cook_time_minutes, d.level, i.name, ri.quantity, ri.linked_at
        FROM recipe_ingredients ri
        JOIN recipes r ON ri.recipe_id = r.id
        JOIN ingredients i ON ri.ingredient_id = i.id
        JOIN difficulty d ON r.difficulty_id = d.id
        ORDER BY r.recipe_name ASC;
    """)
    rows = cur.fetchall()

    if rows:
        st.table([
            {
                "Recipe": r[0],
                "Cuisine": r[1],
                "Cook Time (min)": r[2],
                "Difficulty": r[3],
                "Ingredient": r[4],
                "Quantity": r[5],
                "Linked At": r[6].strftime("%Y-%m-%d %H:%M") if r[6] else ""
            }
            for r in rows
        ])
    else:
        st.info("No data yet. Use the sidebar to add recipes and ingredients!")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
