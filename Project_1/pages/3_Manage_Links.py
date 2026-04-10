import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Recipe-Ingredient Links", page_icon="🔗")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🔗 Manage Recipe-Ingredient Links")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, recipe_name FROM recipes ORDER BY recipe_name;")
    recipes = cur.fetchall()
    cur.execute("SELECT id, name FROM ingredients ORDER BY name;")
    ingredients = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

if not recipes:
    st.warning("No recipes found. Please add recipes first.")
    st.stop()

if not ingredients:
    st.warning("No ingredients found. Please add ingredients first.")
    st.stop()

recipe_options = {r[1]: r[0] for r in recipes}
ingredient_options = {i[1]: i[0] for i in ingredients}

with st.form("add_link_form"):
    selected_recipe = st.selectbox("Select Recipe", list(recipe_options.keys()))
    selected_ingredient = st.selectbox("Select Ingredient", list(ingredient_options.keys()))
    quantity = st.text_input("Quantity (e.g. 2 cups, 1 tbsp)")
    submitted = st.form_submit_button("Link Ingredient to Recipe")

    if submitted:
        if quantity:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity)
                    VALUES (%s, %s, %s);
                    """,
                    (recipe_options[selected_recipe], ingredient_options[selected_ingredient], quantity)
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ Linked '{selected_ingredient}' to '{selected_recipe}' with quantity '{quantity}'!")
            except psycopg2.errors.UniqueViolation:
                st.error("⚠️ That ingredient is already linked to that recipe.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a quantity.")

st.markdown("---")
st.subheader("Current Recipe-Ingredient Links")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.recipe_name, i.name, ri.quantity
        FROM recipe_ingredients ri
        JOIN recipes r ON ri.recipe_id = r.id
        JOIN ingredients i ON ri.ingredient_id = i.id
        ORDER BY r.recipe_name, i.name;
    """)
    links = cur.fetchall()
    cur.close()
    conn.close()

    if links:
        st.table([
            {"Recipe": l[0], "Ingredient": l[1], "Quantity": l[2]}
            for l in links
        ])
    else:
        st.info("No links yet. Use the form above to connect ingredients to recipes!")
except Exception as e:
    st.error(f"Error: {e}")
