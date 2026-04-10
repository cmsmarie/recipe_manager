import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Recipe-Ingredient Links", page_icon="🔗")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🔗 Manage Recipe-Ingredient Links")

# ── Load recipes and ingredients for dropdowns ───────────────────────────────

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

# ── Add Link Form ────────────────────────────────────────────────────────────

st.subheader("Link an Ingredient to a Recipe")
with st.form("add_link_form"):
    selected_recipe = st.selectbox("Select Recipe *", list(recipe_options.keys()))
    selected_ingredient = st.selectbox("Select Ingredient *", list(ingredient_options.keys()))
    quantity = st.text_input("Quantity * (e.g. 2 cups, 1 tbsp)")
    submitted = st.form_submit_button("Link Ingredient to Recipe")

    if submitted:
        errors = []
        if not quantity.strip():
            errors.append("**Quantity** is required.")
        else:
            try:
                qty_num = float(quantity.strip().split()[0])
                if qty_num <= 0:
                    errors.append("**Quantity** must be a positive number.")
            except ValueError:
                pass  # quantity is text like "2 cups" or "1 tbsp" which is fine

        if errors:
            for err in errors:
                st.error(err)
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity)
                    VALUES (%s, %s, %s);
                    """,
                    (recipe_options[selected_recipe], ingredient_options[selected_ingredient], quantity.strip())
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ Linked '{selected_ingredient}' to '{selected_recipe}'!")
                st.rerun()
            except psycopg2.errors.UniqueViolation:
                st.error("⚠️ That ingredient is already linked to that recipe.")
            except Exception as e:
