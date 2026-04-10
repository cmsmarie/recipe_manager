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
    st.error("Error loading data: " + str(e))
    st.stop()

if not recipes:
    st.warning("No recipes found. Please add recipes first.")
    st.stop()

if not ingredients:
    st.warning("No ingredients found. Please add ingredients first.")
    st.stop()

recipe_options = {r[1]: r[0] for r in recipes}
ingredient_options = {i[1]: i[0] for i in ingredients}

st.subheader("Link an Ingredient to a Recipe")
with st.form("add_link_form"):
    selected_recipe = st.selectbox("Select Recipe", list(recipe_options.keys()))
    selected_ingredient = st.selectbox("Select Ingredient", list(ingredient_options.keys()))
    quantity = st.text_input("Quantity (e.g. 2 cups, 1 tbsp)")
    submitted = st.form_submit_button("Link Ingredient to Recipe")

    if submitted:
        errors = []
        if not quantity.strip():
            errors.append("Quantity is required.")
        if not errors:
            first_word = quantity.strip().split()[0]
            is_negative = False
            try:
                qty_num = float(first_word)
                if qty_num <= 0:
                    is_negative = True
            except ValueError:
                is_negative = False
            if is_negative:
                errors.append("Quantity must be a positive number.")
        if errors:
            for err in errors:
                st.error(err)
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (%s, %s, %s);",
                    (recipe_options[selected_recipe], ingredient_options[selected_ingredient], quantity.strip())
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success("Linked " + selected_ingredient + " to " + selected_recipe)
                st.rerun()
            except psycopg2.errors.UniqueViolation:
                st.error("That ingredient is already linked to that recipe.")
            except Exception as e:
                st.error("Error: " + str(e))

st.markdown("---")
st.subheader("Current Recipe-Ingredient Links")
search = st.text_input("Search by recipe or ingredient name")

try:
    conn = get_connection()
    cur = conn.cursor()
    if search.strip():
        cur.execute(
            "SELECT ri.id, r.recipe_name, i.name, ri.quantity, ri.linked_at FROM recipe_ingredients ri JOIN recipes r ON ri.recipe_id = r.id JOIN ingredients i ON ri.ingredient_id = i.id WHERE r.recipe_name ILIKE %s OR i.name ILIKE %s ORDER BY r.recipe_name, i.name;",
            ("%" + search.strip() + "%", "%" + search.strip() + "%")
        )
    else:
        cur.execute(
            "SELECT ri.id, r.recipe_name, i.name, ri.quantity, ri.linked_at FROM recipe_ingredients ri JOIN recipes r ON ri.recipe_id = r.id JOIN ingredients i ON ri.ingredient_id = i.id ORDER BY r.recipe_name, i.name;"
        )
    links = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error("Error: " + str(e))
    st.stop()

if not links:
    st.info("No links found.")
else:
    for l in links:
        lid = l[0]
        lrecipe = l[1]
        lingredient = l[2]
        lqty = l[3]
        ltime = l[4]
        col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 1])
        col1.write(lrecipe)
        col2.write(lingredient)
        col3.write(lqty)
        col4.write(ltime.strftime("%Y-%m-%d %H:%M") if ltime else "")
        key_del = "del_" + str(lid)
        key_yes = "yes_" + str(lid)
        key_no = "no_" + str(lid)
        key_confirm = "confirm_" + str(lid)
        if col5.button("Delete", key=key_del):
            st.session_state[key_confirm] = True
        if st.session_state.get(key_confirm):
            st.warning("Are you sure you want to delete the link between " + lrecipe + " and " + lingredient + "?")
            col_yes, col_no = st.columns(2)
            if col_yes.button("Yes delete it", key=key_yes):
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM recipe_ingredients WHERE id=%s;", (lid,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("Link deleted.")
                    st.session_state[key_confirm] = False
                    st.rerun()
                except Exception as e:
                    st.error("Error: " + str(e))
            if col_no.button("Cancel", key=key_no):
                st.session_state[key_confirm] = False
                st.rerun()
