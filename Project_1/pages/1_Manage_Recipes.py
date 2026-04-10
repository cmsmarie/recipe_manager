import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Recipes", page_icon="📋")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📋 Manage Recipes")

# ── Load difficulty levels from DB (dynamic dropdown) ────────────────────────

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, level FROM difficulty ORDER BY id;")
    difficulty_rows = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error loading difficulty levels: {e}")
    st.stop()

difficulty_options = {row[1]: row[0] for row in difficulty_rows}

# ── Add Recipe Form ──────────────────────────────────────────────────────────

st.subheader("Add a New Recipe")
with st.form("add_recipe_form"):
    recipe_name = st.text_input("Recipe Name *")
    description = st.text_area("Description")
    cuisine = st.text_input("Cuisine *")
    cook_time = st.number_input("Cook Time (minutes) *", min_value=1, step=1)
    difficulty = st.selectbox("Difficulty *", list(difficulty_options.keys()))
    submitted = st.form_submit_button("Add Recipe")

    if submitted:
        errors = []
        if not recipe_name.strip():
            errors.append("**Recipe Name** is required.")
        if not cuisine.strip():
            errors.append("**Cuisine** is required.")
        if cook_time < 1:
            errors.append("**Cook Time** must be a positive number.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO recipes (recipe_name, description, cuisine, cook_time_minutes, difficulty_id)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (recipe_name.strip(), description.strip(), cuisine.strip(), cook_time, difficulty_options[difficulty])
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ Recipe '{recipe_name}' added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ── Search/Filter ────────────────────────────────────────────────────────────

st.subheader("Current Recipes")
search = st.text_input("🔍 Search recipes by name or cuisine")

try:
    conn = get_connection()
    cur = conn.cursor()
    if search.strip():
        cur.execute("""
            SELECT r.id, r.recipe_name, r.cuisine, r.cook_time_minutes, d.level, r.description
            FROM recipes r
            JOIN difficulty d ON r.difficulty_id = d.id
            WHERE r.recipe_name ILIKE %s OR r.cuisine ILIKE %s
            ORDER BY r.recipe_name;
        """, (f"%{search.strip()}%", f"%{search.strip()}%"))
    else:
        cur.execute("""
            SELECT r.id, r.recipe_name, r.cuisine, r.cook_time_minutes, d.level, r.description
            FROM recipes r
            JOIN difficulty d ON r.difficulty_id = d.id
            ORDER BY r.recipe_name;
        """)
    recipes = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

if not recipes:
    st.info("No recipes found.")
else:
    for r in recipes:
        rid, rname, rcuisine, rcook, rdiff, rdesc = r
        with st.expander(f"🍽️ {rname} — {rcuisine} | {rcook} min | {rdiff}"):

            # ── Edit Form ────────────────────────────────────────────────────
            with st.form(f"edit_recipe_{rid}"):
                new_name = st.text_input("Recipe Name *", value=rname)
                new_desc = st.text_area("Description", value=rdesc or "")
                new_cuisine = st.text_input("Cuisine *", value=rcuisine)
                new_cook = st.number_input("Cook Time (minutes) *", min_value=1, step=1, value=rcook)
                new_diff = st.selectbox(
                    "Difficulty *",
                    list(difficulty_options.keys()),
                    index=list(difficulty_options.keys()).index(rdiff)
                )
                update = st.form_submit_button("💾 Save Changes")

                if update:
                    errors = []
                    if not new_name.strip():
                        errors.append("**Recipe Name** is required.")
                    if not new_cuisine.strip():
                        errors.append("**Cuisine** is required.")
                    if new_cook < 1:
                        errors.append("**Cook Time** must be a positive number.")

                    if errors:
                        for err in errors:
                            st.error(err)
                    else:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute(
                                """
                                UPDATE recipes
                                SET recipe_name=%s, description=%s, cuisine=%s,
                                    cook_time_minutes=%s, difficulty_id=%s
                                WHERE id=%s;
                                """,
                                (new_name.strip(), new_desc.strip(), new_cuisine.strip(),
                                 new_cook, difficulty_options[new_diff], rid)
                            )
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success("✅ Recipe updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

            # ── Delete with confirmation ──────────────────────────────────────
            st.warning(f"⚠️ Deleting '{rname}' will also remove all its ingredient links.")
            confirm = st.checkbox(f"Yes, I want to delete '{rname}'", key=f"confirm_del_recipe_{rid}")
            if confirm:
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
