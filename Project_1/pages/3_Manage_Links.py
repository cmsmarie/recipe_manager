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
                st.success(f"✅ Linked '{selected_ingredient}' to '{selected_recipe}'!")
                st.rerun()
            except psycopg2.errors.UniqueViolation:
                st.error("⚠️ That ingredient is already linked to that recipe.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a quantity.")

st.markdown("---")

# ── Current Links Table with Delete ─────────────────────────────────────────

st.subheader("Current Recipe-Ingredient Links")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ri.id, r.recipe_name, i.name, ri.quantity
        FROM recipe_ingredients ri
        JOIN recipes r ON ri.recipe_id = r.id
        JOIN ingredients i ON ri.ingredient_id = i.id
        ORDER BY r.recipe_name, i.name;
    """)
    links = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

if not links:
    st.info("No links yet. Use the form above to connect ingredients to recipes!")
else:
    for l in links:
        lid, lrecipe, lingredient, lqty = l
        col1, col2, col3, col4 = st.columns([3, 3, 2, 1])
        col1.write(lrecipe)
        col2.write(lingredient)
        col3.write(lqty)
        if col4.button("🗑️", key=f"del_link_{lid}"):
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM recipe_ingredients WHERE id=%s;", (lid,))
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ Link deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
