import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Recipes", page_icon="📋")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📋 Manage Recipes")

# ── Add Recipe Form ──────────────────────────────────────────────────────────

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

# ── Current Recipes Table with Edit and Delete ───────────────────────────────

st.subheader("Current Recipes")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, recipe_name, cuisine, cook_time_minutes, difficulty, description FROM recipes ORDER BY recipe_name;")
    recipes = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

if not recipes:
    st.info("No recipes yet.")
else:
    for r in recipes:
        rid, rname, rcuisine, rcook, rdiff, rdesc = r
        with st.expander(f"🍽️ {rname} — {rcuisine} | {rcook} min | {rdiff}"):

            # ── Edit Form ────────────────────────────────────────────────────
            with st.form(f"edit_recipe_{rid}"):
                new_name = st.text_input("Recipe Name", value=rname)
                new_desc = st.text_area("Description", value=rdesc or "")
                new_cuisine = st.text_input("Cuisine", value=rcuisine)
                new_cook = st.number_input("Cook Time (minutes)", min_value=1, step=1, value=rcook)
                new_diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=["Easy", "Medium", "Hard"].index(rdiff))
                update = st.form_submit_button("💾 Save Changes")

                if update:
                    if new_name and new_cuisine and new_diff:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute(
                                """
                                UPDATE recipes
                                SET recipe_name=%s, description=%s, cuisine=%s, cook_time_minutes=%s, difficulty=%s
                                WHERE id=%s;
                                """,
                                (new_name, new_desc, new_cuisine, new_cook, new_diff, rid)
                            )
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success("✅ Recipe updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Please fill in all required fields.")

            # ── Delete Button ────────────────────────────────────────────────
            if st.button(f"🗑️ Delete '{rname}'", key=f"del_recipe_{rid}"):
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM recipes WHERE id=%s;", (rid,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"✅ Recipe '{rname}' deleted.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
