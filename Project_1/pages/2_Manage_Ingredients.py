import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Ingredients", page_icon="🥕")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🥕 Manage Ingredients")

with st.form("add_ingredient_form"):
    name = st.text_input("Ingredient Name")
    category = st.text_input("Category (e.g. Dairy, Protein, Vegetable)")
    submitted = st.form_submit_button("Add Ingredient")

    if submitted:
        if name and category:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO ingredients (name, category) VALUES (%s, %s);",
                    (name, category)
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ Ingredient '{name}' added successfully!")
            except psycopg2.errors.UniqueViolation:
                st.error("⚠️ That ingredient already exists.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please fill in both fields.")

st.markdown("---")
st.subheader("Current Ingredients")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, category FROM ingredients ORDER BY name;")
    ingredients = cur.fetchall()
    cur.close()
    conn.close()

    if ingredients:
        st.table([
            {"ID": i[0], "Ingredient": i[1], "Category": i[2]}
            for i in ingredients
        ])
    else:
        st.info("No ingredients yet.")
except Exception as e:
    st.error(f"Error: {e}")
