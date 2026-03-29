import streamlit as st
import json
import uuid
import time
from datetime import datetime
from data import CATEGORIES, CATEGORY_COLORS, UNITS, INDIAN_STAPLES, STARTER_ITEMS, RECIPES

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Rasoi Manager 🍛",
    page_icon="🍛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  — edit colors here
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #3D2DB5 !important;
}
[data-testid="stSidebar"] * {
    color: white !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 15px !important;
    padding: 6px 0 !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #EEECFF;
    border-radius: 14px;
    padding: 16px !important;
    border: 1px solid rgba(61,45,181,0.15);
}
[data-testid="stMetricLabel"] { color: #3D2DB5 !important; font-weight: 600 !important; }
[data-testid="stMetricValue"] { color: #3D2DB5 !important; }

/* ── Buttons ── */
.stButton > button {
    background: #3D2DB5 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── Item card ── */
.item-card {
    background: white;
    border: 1px solid rgba(100,60,180,0.15);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.item-card.low {
    border-color: rgba(232,96,10,0.35);
    background: #FFFAF7;
}

/* ── Recipe card ── */
.recipe-card {
    background: white;
    border: 1px solid rgba(100,60,180,0.15);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    transition: box-shadow 0.2s;
}
.recipe-card:hover { box-shadow: 0 2px 12px rgba(61,45,181,0.1); }

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}
.badge-low   { background: #FFF0E8; color: #B84800; }
.badge-easy  { background: #E3F8F2; color: #085041; }
.badge-medium{ background: #FFF8E1; color: #7A4800; }
.badge-hard  { background: #FCE4EC; color: #880E4F; }
.badge-have  { background: #EEECFF; color: #3D2DB5; }
.badge-miss  { background: #FFF0E8; color: #B84800; }

/* ── Progress bar override ── */
.stProgress > div > div { background: #3D2DB5 !important; }

/* ── Section title ── */
.sec-title {
    font-size: 17px;
    font-weight: 700;
    color: #1E1040;
    margin: 20px 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 2px solid #EEECFF;
}

/* ── Alert box ── */
.alert-box {
    background: #FFF0E8;
    border: 1px solid rgba(232,96,10,0.3);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* ── Shop item ── */
.shop-item {
    background: white;
    border: 1px solid rgba(100,60,180,0.15);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 7px;
}

/* ── Hide streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Expander ── */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    background: #F7F3FF !important;
    border-radius: 10px !important;
}

/* ── Selectbox / input ── */
.stSelectbox > div > div, .stNumberInput > div > div > input, .stTextInput > div > div > input {
    border-color: rgba(100,60,180,0.3) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  STATE MANAGEMENT
# ─────────────────────────────────────────────
def init_state():
    if "pantry" not in st.session_state:
        # Seed starter items on first load
        starter = []
        low_demo = {"Toor Dal", "Ghee", "Onions", "Tea Leaves"}
        for s in INDIAN_STAPLES:
            if s["name"] in STARTER_ITEMS:
                item = s.copy()
                item["id"] = str(uuid.uuid4())
                item["added"] = datetime.now().isoformat()
                if item["name"] in low_demo:
                    item["qty"] = round(item["thresh"] * 0.4, 2)
                starter.append(item)
        st.session_state.pantry = starter

    if "shopping" not in st.session_state:
        st.session_state.shopping = []

    if "page" not in st.session_state:
        st.session_state.page = "🏠 Dashboard"


def get_pantry():
    return st.session_state.pantry


def get_cat_info(cat_id):
    return next((c for c in CATEGORIES if c["id"] == cat_id), {"label": cat_id, "emoji": "📦"})


def is_low(item):
    return item["qty"] <= item["thresh"]


def sync_shopping():
    """Auto-add low stock items to shopping list."""
    pantry = get_pantry()
    shop = st.session_state.shopping
    existing_sources = {s["source_id"] for s in shop if s.get("auto")}
    low_ids = {i["id"] for i in pantry if is_low(i)}

    # Add newly low items
    for item in pantry:
        if is_low(item) and item["id"] not in existing_sources:
            shop.append({
                "id": str(uuid.uuid4()),
                "name": item["name"],
                "cat": item["cat"],
                "auto": True,
                "checked": False,
                "source_id": item["id"],
            })

    # Remove auto items that are no longer low
    st.session_state.shopping = [
        s for s in shop
        if not s.get("auto") or s.get("source_id") in low_ids
    ]


# ─────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🍛 Rasoi Manager")
        st.markdown("*Your Indian kitchen pantry*")
        st.markdown("---")

        pages = ["🏠 Dashboard", "📦 Pantry", "🛒 Shopping List", "🍽️ Recipes", "➕ Add Item"]
        page = st.radio("Navigate", pages, index=pages.index(st.session_state.page), label_visibility="collapsed")
        st.session_state.page = page

        st.markdown("---")
        pantry = get_pantry()
        low = [i for i in pantry if is_low(i)]
        st.markdown(f"**{len(pantry)}** items in pantry")
        if low:
            st.markdown(f"⚠️ **{len(low)}** items low")
        else:
            st.markdown("✅ All stocked!")

        st.markdown("---")
        st.markdown("*Edit `data.py` to add recipes & ingredients*")


# ─────────────────────────────────────────────
#  DASHBOARD PAGE
# ─────────────────────────────────────────────
def page_dashboard():
    st.markdown("# 🏠 Dashboard")
    st.markdown(f"*Good day! Here's your kitchen at a glance — {datetime.now().strftime('%d %B %Y')}*")

    pantry = get_pantry()
    sync_shopping()
    low = [i for i in pantry if is_low(i)]
    cats_used = len(set(i["cat"] for i in pantry))
    shop_count = len(st.session_state.shopping)

    # ── Stat cards ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Total Items", len(pantry))
    c2.metric("⚠️ Low Stock", len(low))
    c3.metric("🗂️ Categories", cats_used)
    c4.metric("🛒 Shopping List", shop_count)

    st.markdown("---")

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        # ── Low stock alerts ──
        st.markdown('<div class="sec-title">⚠️ Needs Restocking</div>', unsafe_allow_html=True)
        if not low:
            st.success("✅ Your pantry is fully stocked!")
        else:
            for item in low[:6]:
                cat = get_cat_info(item["cat"])
                pct = min(100, int((item["qty"] / (item["thresh"] * 4)) * 100))
                st.markdown(f"""
                <div class="alert-box">
                    <span style="font-size:20px">{cat['emoji']}</span>
                    <div style="flex:1">
                        <strong>{item['name']}</strong> is running low &nbsp;
                        <span class="badge badge-low">Low stock</span><br>
                        <span style="color:#7B6F8A;font-size:12px">{cat['label']} · {item['qty']} {item['unit']} left</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(max(pct, 5) / 100)

            if len(low) > 6:
                st.info(f"+ {len(low) - 6} more items need restocking. Go to Pantry →")

    with col_right:
        # ── Category breakdown ──
        st.markdown('<div class="sec-title">🗂️ Category Breakdown</div>', unsafe_allow_html=True)
        from collections import Counter
        cat_counts = Counter(i["cat"] for i in pantry)
        for cat in CATEGORIES:
            if cat["id"] in cat_counts:
                count = cat_counts[cat["id"]]
                low_in_cat = sum(1 for i in pantry if i["cat"] == cat["id"] and is_low(i))
                col_a, col_b = st.columns([3, 1])
                col_a.markdown(f"{cat['emoji']} **{cat['label']}** — {count} items"
                               + (f" ⚠️ {low_in_cat} low" if low_in_cat else ""))
                col_b.markdown(f"")

        st.markdown("---")
        # ── Quick add from recent ──
        st.markdown('<div class="sec-title">⏱️ Recently Added</div>', unsafe_allow_html=True)
        recent = sorted(pantry, key=lambda x: x.get("added", ""), reverse=True)[:5]
        for item in recent:
            cat = get_cat_info(item["cat"])
            st.markdown(f"{cat['emoji']} **{item['name']}** — {item['qty']} {item['unit']}")


# ─────────────────────────────────────────────
#  PANTRY PAGE
# ─────────────────────────────────────────────
def page_pantry():
    st.markdown("# 📦 Pantry")

    pantry = get_pantry()

    # ── Filters ──
    col_search, col_cat, col_filter = st.columns([2, 1.5, 1])
    with col_search:
        search = st.text_input("🔍 Search items", placeholder="e.g. Dal, Rice, Ghee...", label_visibility="collapsed")
    with col_cat:
        cat_options = ["All Categories"] + [f"{c['emoji']} {c['label']}" for c in CATEGORIES if any(i["cat"] == c["id"] for i in pantry)]
        selected_cat = st.selectbox("Category", cat_options, label_visibility="collapsed")
    with col_filter:
        show_low = st.checkbox("⚠️ Low stock only")

    # ── Apply filters ──
    filtered = pantry
    if search:
        filtered = [i for i in filtered if search.lower() in i["name"].lower()]
    if selected_cat != "All Categories":
        cat_id = next((c["id"] for c in CATEGORIES if f"{c['emoji']} {c['label']}" == selected_cat), None)
        if cat_id:
            filtered = [i for i in filtered if i["cat"] == cat_id]
    if show_low:
        filtered = [i for i in filtered if is_low(i)]

    st.markdown(f"*Showing {len(filtered)} of {len(pantry)} items*")
    st.markdown("---")

    if not filtered:
        st.info("No items found. Try adjusting your filters or add items via ➕ Add Item.")
        return

    # ── Item list ──
    for item in filtered:
        cat = get_cat_info(item["cat"])
        low = is_low(item)
        pct = min(100, int((item["qty"] / (item["thresh"] * 4)) * 100))
        color = CATEGORY_COLORS.get(item["cat"], "#F5F5F5")

        with st.container():
            col1, col2, col3, col4 = st.columns([0.4, 3, 2, 1.5])

            with col1:
                st.markdown(f'<div style="background:{color};border-radius:10px;width:44px;height:44px;display:flex;align-items:center;justify-content:center;font-size:22px;margin-top:4px">{cat["emoji"]}</div>', unsafe_allow_html=True)

            with col2:
                low_badge = '<span class="badge badge-low">Low stock</span>' if low else ""
                st.markdown(f"**{item['name']}** {low_badge}", unsafe_allow_html=True)
                st.markdown(f'<span style="color:#7B6F8A;font-size:12px">{cat["label"]}</span>', unsafe_allow_html=True)
                st.progress(max(pct, 3) / 100)

            with col3:
                qcol1, qcol2, qcol3 = st.columns([1, 1.2, 1])
                with qcol1:
                    if st.button("−", key=f"dec_{item['id']}"):
                        item["qty"] = max(0, round(item["qty"] - 1, 2))
                        sync_shopping()
                        st.rerun()
                with qcol2:
                    st.markdown(f'<div style="text-align:center;padding-top:6px"><strong style="font-size:16px">{item["qty"]}</strong><br><span style="font-size:11px;color:#7B6F8A">{item["unit"]}</span></div>', unsafe_allow_html=True)
                with qcol3:
                    if st.button("+", key=f"inc_{item['id']}"):
                        item["qty"] = round(item["qty"] + 1, 2)
                        sync_shopping()
                        st.rerun()

            with col4:
                if st.button("🗑 Remove", key=f"del_{item['id']}"):
                    st.session_state.pantry = [i for i in st.session_state.pantry if i["id"] != item["id"]]
                    st.rerun()

            st.markdown('<hr style="margin:6px 0;border:none;border-top:1px solid rgba(100,60,180,0.08)">', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SHOPPING LIST PAGE
# ─────────────────────────────────────────────
def page_shopping():
    st.markdown("# 🛒 Shopping List")
    sync_shopping()
    shop = st.session_state.shopping

    done = sum(1 for s in shop if s["checked"])
    st.markdown(f"*{done}/{len(shop)} items done*")

    col_add, col_clear, col_refresh = st.columns([2, 1, 1])
    with col_add:
        manual_name = st.text_input("Add item manually", placeholder="Type item name and press Enter", label_visibility="collapsed")
        if manual_name:
            st.session_state.shopping.append({
                "id": str(uuid.uuid4()),
                "name": manual_name,
                "cat": "other",
                "auto": False,
                "checked": False,
            })
            st.rerun()
    with col_clear:
        if st.button("✓ Clear done"):
            st.session_state.shopping = [s for s in shop if not s["checked"]]
            st.rerun()
    with col_refresh:
        if st.button("↺ Refresh"):
            sync_shopping()
            st.rerun()

    st.markdown("---")

    if not shop:
        st.info("🛒 Your list is empty! Low stock items appear here automatically. Add items manually above.")
        return

    auto_items = [s for s in shop if s.get("auto")]
    manual_items = [s for s in shop if not s.get("auto")]

    if auto_items:
        st.markdown('<div class="sec-title">🤖 Auto-suggested (Low Stock)</div>', unsafe_allow_html=True)
        for item in auto_items:
            render_shop_item(item)

    if manual_items:
        st.markdown('<div class="sec-title">✍️ Added by You</div>', unsafe_allow_html=True)
        for item in manual_items:
            render_shop_item(item)


def render_shop_item(item):
    cat = get_cat_info(item["cat"])
    col1, col2, col3 = st.columns([0.3, 4, 1])
    with col1:
        checked = st.checkbox("", value=item["checked"], key=f"chk_{item['id']}")
        if checked != item["checked"]:
            item["checked"] = checked
            st.rerun()
    with col2:
        style = "text-decoration:line-through;color:#AAA" if item["checked"] else "color:#1E1040"
        auto_badge = '<span class="badge badge-low" style="font-size:10px">low stock</span>' if item.get("auto") else ""
        st.markdown(f'<span style="{style};font-weight:600">{item["name"]}</span> {auto_badge}<br><span style="color:#7B6F8A;font-size:12px">{cat["emoji"]} {cat["label"]}</span>', unsafe_allow_html=True)
    with col3:
        if st.button("✕", key=f"rm_{item['id']}"):
            st.session_state.shopping = [s for s in st.session_state.shopping if s["id"] != item["id"]]
            st.rerun()
    st.markdown('<hr style="margin:4px 0;border:none;border-top:1px solid rgba(100,60,180,0.07)">', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  RECIPES PAGE
# ─────────────────────────────────────────────
def page_recipes():
    st.markdown("# 🍽️ Recipe Ideas")
    st.markdown("*Recipes scored based on what's in your pantry right now*")

    pantry_names = {i["name"] for i in get_pantry()}

    # Score recipes
    scored = []
    for r in RECIPES:
        have = [n for n in r["needs"] if n in pantry_names]
        miss = [n for n in r["needs"] if n not in pantry_names]
        score = int((len(have) / len(r["needs"])) * 100)
        scored.append({**r, "have": have, "miss": miss, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)

    # ── Filters ──
    col_search, col_region, col_diff = st.columns(3)
    with col_search:
        search = st.text_input("🔍 Search recipes", placeholder="e.g. Dal, Biryani...", label_visibility="collapsed")
    with col_region:
        regions = ["All Regions"] + sorted(set(r["region"] for r in RECIPES))
        region = st.selectbox("Region", regions, label_visibility="collapsed")
    with col_diff:
        diffs = ["All Difficulties", "Easy", "Medium", "Hard"]
        diff = st.selectbox("Difficulty", diffs, label_visibility="collapsed")

    filtered = scored
    if search:
        filtered = [r for r in filtered if search.lower() in r["name"].lower()]
    if region != "All Regions":
        filtered = [r for r in filtered if r["region"] == region]
    if diff != "All Difficulties":
        filtered = [r for r in filtered if r["difficulty"] == diff]

    st.markdown("---")

    can_make = [r for r in filtered if r["score"] == 100]
    almost   = [r for r in filtered if 50 <= r["score"] < 100]
    need_more= [r for r in filtered if r["score"] < 50]

    def render_section(title, recipes):
        if not recipes:
            return
        st.markdown(f'<div class="sec-title">{title}</div>', unsafe_allow_html=True)
        for recipe in recipes:
            render_recipe_card(recipe)

    render_section("✅ Ready to cook now", can_make)
    render_section("🛒 Almost there", almost)
    render_section("📦 Need more ingredients", need_more)

    if not filtered:
        st.info("No recipes found. Try adjusting your filters or add more items to your pantry.")


def render_recipe_card(recipe):
    diff_class = {"Easy": "badge-easy", "Medium": "badge-medium", "Hard": "badge-hard"}.get(recipe["difficulty"], "badge-easy")
    score_color = "#0D9E6E" if recipe["score"] == 100 else "#D4A017" if recipe["score"] >= 50 else "#E8600A"

    with st.expander(f"{recipe['emoji']} **{recipe['name']}** — {recipe['score']}% match · {recipe['time']} · {recipe['region']}"):
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(f'<span class="badge {diff_class}">{recipe["difficulty"]}</span>&nbsp;&nbsp;⏱ {recipe["time"]}&nbsp;&nbsp;👥 {recipe["servings"]} servings', unsafe_allow_html=True)
            st.markdown(f"**Pantry match:** {recipe['score']}%")
            st.progress(recipe["score"] / 100)

            st.markdown("**You have:**")
            for ing in recipe["have"]:
                st.markdown(f'<span class="badge badge-have">✅ {ing}</span> ', unsafe_allow_html=True)

            if recipe["miss"]:
                st.markdown("**You need:**")
                for ing in recipe["miss"]:
                    st.markdown(f'<span class="badge badge-miss">🛒 {ing}</span> ', unsafe_allow_html=True)

                if st.button(f"Add missing to shopping list", key=f"add_miss_{recipe['id']}"):
                    for ing in recipe["miss"]:
                        already = any(s["name"] == ing for s in st.session_state.shopping)
                        if not already:
                            st.session_state.shopping.append({
                                "id": str(uuid.uuid4()),
                                "name": ing,
                                "cat": "other",
                                "auto": False,
                                "checked": False,
                            })
                    st.success(f"Added {len(recipe['miss'])} items to shopping list!")

        with col2:
            st.markdown("**Steps:**")
            for i, step in enumerate(recipe["steps"], 1):
                st.markdown(f"**{i}.** {step}")


# ─────────────────────────────────────────────
#  ADD ITEM PAGE
# ─────────────────────────────────────────────
def page_add_item():
    st.markdown("# ➕ Add Item to Pantry")

    pantry_names = {i["name"] for i in get_pantry()}
    available_staples = [s for s in INDIAN_STAPLES if s["name"] not in pantry_names]

    # ── Quick pick ──
    st.markdown('<div class="sec-title">⚡ Quick Pick — Indian Staples</div>', unsafe_allow_html=True)
    st.markdown("*Click any item to auto-fill the form below:*")

    staple_names = [s["name"] for s in available_staples[:30]]
    selected_quick = st.selectbox("Select a staple to quick-fill", ["— choose —"] + staple_names, label_visibility="collapsed")

    quick_data = None
    if selected_quick != "— choose —":
        quick_data = next((s for s in available_staples if s["name"] == selected_quick), None)

    st.markdown("---")
    st.markdown('<div class="sec-title">📝 Item Details</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        default_name = quick_data["name"] if quick_data else ""
        name = st.text_input("Item name *", value=default_name, placeholder="e.g. Basmati Rice")

        cat_labels = [f"{c['emoji']} {c['label']}" for c in CATEGORIES]
        default_cat_idx = 0
        if quick_data:
            default_cat_idx = next((i for i, c in enumerate(CATEGORIES) if c["id"] == quick_data["cat"]), 0)
        selected_cat_label = st.selectbox("Category", cat_labels, index=default_cat_idx)
        selected_cat_id = CATEGORIES[cat_labels.index(selected_cat_label)]["id"]

    with col2:
        default_qty = float(quick_data["qty"]) if quick_data else 1.0
        qty = st.number_input("Quantity", min_value=0.0, value=default_qty, step=0.5)

        default_unit_idx = UNITS.index(quick_data["unit"]) if quick_data and quick_data["unit"] in UNITS else 0
        unit = st.selectbox("Unit", UNITS, index=default_unit_idx)

        default_thresh = float(quick_data["thresh"]) if quick_data else 1.0
        thresh = st.number_input("Low stock alert when below", min_value=0.0, value=default_thresh, step=0.5)

    st.markdown("")
    col_btn1, col_btn2, _ = st.columns([1, 1, 3])

    with col_btn1:
        if st.button("✅ Add to Pantry", use_container_width=True):
            if not name.strip():
                st.error("Please enter an item name.")
            else:
                new_item = {
                    "id": str(uuid.uuid4()),
                    "name": name.strip(),
                    "cat": selected_cat_id,
                    "qty": round(qty, 2),
                    "unit": unit,
                    "thresh": round(thresh, 2),
                    "added": datetime.now().isoformat(),
                }
                st.session_state.pantry.insert(0, new_item)
                sync_shopping()
                st.success(f"✅ **{name}** added to pantry!")
                st.balloons()

    with col_btn2:
        if st.button("🔄 Reset Form", use_container_width=True):
            st.rerun()

    # ── Bulk add section ──
    st.markdown("---")
    st.markdown('<div class="sec-title">📋 Bulk Add Common Staples</div>', unsafe_allow_html=True)
    st.markdown("*Select multiple items to add at once with default quantities:*")

    available_names = [s["name"] for s in available_staples]
    selected_bulk = st.multiselect("Choose items to add", available_names, placeholder="Select Indian staples...")

    if selected_bulk:
        st.markdown(f"*{len(selected_bulk)} items selected*")
        if st.button(f"➕ Add {len(selected_bulk)} Items to Pantry"):
            added_count = 0
            for sname in selected_bulk:
                staple = next((s for s in available_staples if s["name"] == sname), None)
                if staple:
                    new_item = {
                        **staple,
                        "id": str(uuid.uuid4()),
                        "added": datetime.now().isoformat(),
                    }
                    st.session_state.pantry.insert(0, new_item)
                    added_count += 1
            sync_shopping()
            st.success(f"✅ Added {added_count} items to your pantry!")
            st.rerun()


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    init_state()
    render_sidebar()

    page = st.session_state.page

    if page == "🏠 Dashboard":
        page_dashboard()
    elif page == "📦 Pantry":
        page_pantry()
    elif page == "🛒 Shopping List":
        page_shopping()
    elif page == "🍽️ Recipes":
        page_recipes()
    elif page == "➕ Add Item":
        page_add_item()


if __name__ == "__main__":
    main()
