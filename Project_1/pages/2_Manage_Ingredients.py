import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Ingredients", page_icon="🥕")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🥕 Manage Ingredients")

# ── Add Ingredient Form ──────────────────────────────────────────────────────

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

# ── Current Ingredients Table with Edit and Delete ───────────────────────────

st.subheader("Current Ingredients")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, category FROM ingredients ORDER BY name;")
    ingredients = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

if not ingredients:
    st.info("No ingredients yet.")
else:
    for i in ingredients:
        iid, iname, icat = i
        with st.expander(f"🥕 {iname} — {icat}"):

            # ── Edit Form ────────────────────────────────────────────────────
            with st.form(f"edit_ingredient_{iid}"):
                new_name = st.text_input("Ingredient Name", value=iname)
                new_cat = st.text_input("Category", value=icat)
                update = st.form_submit_button("💾 Save Changes")

                if update:
                    if new_name and new_cat:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute(
                                "UPDATE ingredients SET name=%s, category=%s WHERE id=%s;",
                                (new_name, new_cat, iid)
                            )
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success("✅ Ingredient updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Please fill in both fields.")

            # ── Delete Button ────────────────────────────────────────────────
            if st.button(f"🗑️ Delete '{iname}'", key=f"del_ingredient_{iid}"):
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM ingredients WHERE id=%s;", (iid,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"✅ Ingredient '{iname}' deleted.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
