import streamlit as st
import json
import uuid
import os
from datetime import datetime
from data import CATEGORIES, CATEGORY_COLORS, UNITS, INDIAN_STAPLES, STARTER_ITEMS, RECIPES

st.set_page_config(
    page_title="Rasoi Manager 🍛",
    page_icon="🍛",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background: #F7F3FF; }

/* Hide sidebar & chrome */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarToggle"],
.st-emotion-cache-1rtdyuf,
.st-emotion-cache-pkbazv { display: none !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }

/* Content area */
.main .block-container {
    padding: 0 10px 100px 10px !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}

/* Top bar */
.top-bar {
    background: #3D2DB5;
    margin: 0 -10px 16px -10px;
    padding: 14px 18px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.top-bar-title { color: white; font-size: 18px; font-weight: 700; margin: 0; }
.top-bar-sub   { color: rgba(255,255,255,0.72); font-size: 12px; margin: 2px 0 0; }
.top-bar-user  {
    background: rgba(255,255,255,0.2); border-radius: 20px;
    padding: 4px 12px; color: white; font-size: 12px; font-weight: 500;
}

/* ── Bottom nav container ── */
.nav-wrapper {
    position: fixed;
    bottom: 0; left: 50%;
    transform: translateX(-50%);
    width: 100%; max-width: 480px;
    background: white;
    border-top: 1.5px solid rgba(61,45,181,0.12);
    box-shadow: 0 -4px 20px rgba(61,45,181,0.1);
    z-index: 999;
    padding: 4px 0 8px;
}

/* Style the Streamlit columns inside nav */
.nav-wrapper [data-testid="column"] {
    padding: 0 2px !important;
}

/* Nav buttons */
.nav-wrapper .stButton > button {
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 6px 2px 4px !important;
    font-size: 10px !important;
    font-weight: 500 !important;
    color: #AAA0BB !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 2px !important;
    min-height: 52px !important;
    box-shadow: none !important;
}
.nav-wrapper .stButton > button:hover {
    background: #F0ECFF !important;
    color: #3D2DB5 !important;
}

/* Active nav button override — we use a data attr trick via class */
div[data-nav-active="true"] .stButton > button {
    color: #3D2DB5 !important;
    font-weight: 700 !important;
    background: #EEECFF !important;
}

/* General buttons */
section.main .stButton > button {
    background: #3D2DB5 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
section.main .stButton > button[kind="secondary"] {
    background: white !important;
    color: #3D2DB5 !important;
    border: 1.5px solid rgba(61,45,181,0.3) !important;
}

/* Stat grid */
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px; }
.stat-card { border-radius: 14px; padding: 14px 16px; border: 1px solid rgba(100,60,180,0.12); }
.stat-lbl  { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing:.05em; margin-bottom:4px; }
.stat-val  { font-size: 28px; font-weight: 700; line-height: 1.1; }

/* Alert / item cards */
.alert-card {
    background: #FFF0E8; border: 1px solid rgba(232,96,10,.25);
    border-radius: 12px; padding: 11px 13px; margin-bottom: 8px;
}
.sec-title {
    font-size: 15px; font-weight: 700; color: #1E1040;
    margin: 16px 0 10px; padding-bottom: 5px;
    border-bottom: 2px solid #EEECFF;
}

/* Badges */
.badge { display:inline-block; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:600; }
.badge-low    { background:#FFF0E8; color:#B84800; }
.badge-easy   { background:#E3F8F2; color:#085041; }
.badge-medium { background:#FFF8E1; color:#7A4800; }
.badge-hard   { background:#FCE4EC; color:#880E4F; }
.badge-have   { background:#EEECFF; color:#3D2DB5; }
.badge-miss   { background:#FFF0E8; color:#B84800; }

/* Cat icon */
.cat-icon {
    width:42px; height:42px; border-radius:10px;
    display:flex; align-items:center; justify-content:center;
    font-size:20px; flex-shrink:0;
}

/* Login */
.login-wrap { background:white; border-radius:20px; padding:28px 22px; border:1px solid rgba(100,60,180,.15); margin-top:12px; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox > div > div {
    border-color: rgba(100,60,180,.25) !important; border-radius:10px !important;
}
.stProgress > div > div { background: #3D2DB5 !important; }
.streamlit-expanderHeader { background:#F0ECFF !important; border-radius:10px !important; font-weight:600 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────
#  CONFIG  ✏️ Edit to add households
# ─────────────────────────────────────
HOUSEHOLDS = {
    "🏠 Aulakh Family":  {"password": "Khanakhazana@1826",  "color": "#E8600A"},
    "🏡 Khangura Family": {"password": "Khangura123", "color": "#0D9E6E"},
}
MEMBERS = {
    "🏠 Aulakh Family":  ["Sach", "Sukh", "Aayaan"],
    "🏡 Khangura Family": ["Manpreet", "Honey", "Rabaab"],
    }
NAV = [
    ("home",    "🏠", "Home"),
    ("pantry",  "📦", "Pantry"),
    ("shop",    "🛒", "Shop"),
    ("recipes", "🍽️", "Recipes"),
    ("add",     "➕", "Add"),
]
PAGE_META = {
    "home":    ("🏠", "Dashboard",   "Your kitchen at a glance"),
    "pantry":  ("📦", "Pantry",      "Manage your stock"),
    "shop":    ("🛒", "Shopping",    "Your shopping list"),
    "recipes": ("🍽️", "Recipes",     "What can you cook?"),
    "add":     ("➕", "Add Item",    "Add to your pantry"),
}


# ─────────────────────────────────────
#  DATA HELPERS
# ─────────────────────────────────────
DATA_DIR = "data_store"
os.makedirs(DATA_DIR, exist_ok=True)

def dpath(hh, t):
    safe = "".join(c for c in hh if c.isalnum() or c in "_-")
    return os.path.join(DATA_DIR, f"{safe}_{t}.json")

def load_j(path, default):
    try:
        if os.path.exists(path):
            with open(path) as f: return json.load(f)
    except: pass
    return default

def save_j(path, obj):
    with open(path, "w") as f: json.dump(obj, f, indent=2)

def save_pantry():   save_j(dpath(st.session_state.household, "pantry"),   st.session_state.pantry)
def save_shopping(): save_j(dpath(st.session_state.household, "shopping"), st.session_state.shopping)

def get_cat(cid): return next((c for c in CATEGORIES if c["id"] == cid), {"label": cid, "emoji": "📦"})
def is_low(item): return item["qty"] <= item["thresh"]

def sync_shop():
    pantry, shop = st.session_state.pantry, st.session_state.shopping
    existing = {s["source_id"] for s in shop if s.get("auto")}
    low_ids  = {i["id"] for i in pantry if is_low(i)}
    for item in pantry:
        if is_low(item) and item["id"] not in existing:
            shop.append({"id": str(uuid.uuid4()), "name": item["name"],
                         "cat": item["cat"], "auto": True, "checked": False,
                         "source_id": item["id"],
                         "added_by": st.session_state.get("member","")})
    st.session_state.shopping = [s for s in shop if not s.get("auto") or s.get("source_id") in low_ids]
    save_shopping()

def seed(member):
    low_demo = {"Toor Dal","Ghee","Onions","Tea Leaves"}
    out = []
    for s in INDIAN_STAPLES:
        if s["name"] in STARTER_ITEMS:
            item = {**s, "id": str(uuid.uuid4()),
                    "added": datetime.now().isoformat(), "added_by": member}
            if item["name"] in low_demo: item["qty"] = round(item["thresh"]*0.4, 2)
            out.append(item)
    return out

def do_login(hh, member):
    st.session_state.update({"logged_in":True,"household":hh,"member":member,"tab":"home"})
    pantry = load_j(dpath(hh,"pantry"), [])
    if not pantry:
        pantry = seed(member)
        save_j(dpath(hh,"pantry"), pantry)
    st.session_state.pantry   = pantry
    st.session_state.shopping = load_j(dpath(hh,"shopping"), [])
    st.rerun()


# ─────────────────────────────────────
#  TOP BAR
# ─────────────────────────────────────
def top_bar():
    tab    = st.session_state.get("tab","home")
    icon, title, sub = PAGE_META.get(tab, ("🍛","Rasoi",""))
    member = st.session_state.get("member","")
    st.markdown(f"""
    <div class="top-bar">
        <div>
            <div class="top-bar-title">{icon} {title}</div>
            <div class="top-bar-sub">{sub}</div>
        </div>
        <div class="top-bar-user">👤 {member}</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────
#  BOTTOM NAV  — pure Streamlit buttons
# ─────────────────────────────────────
def bottom_nav():
    cur = st.session_state.get("tab","home")

    # Inject a wrapper div so we can CSS-target it
    st.markdown('<div class="nav-wrapper" id="bottom-nav">', unsafe_allow_html=True)
    cols = st.columns(len(NAV))
    for i, (key, icon, label) in enumerate(NAV):
        with cols[i]:
            # Show active state with a marker in the label
            if cur == key:
                btn_label = f"{icon}\n**{label}**\n·"
            else:
                btn_label = f"{icon}\n{label}"
            if st.button(btn_label, key=f"nav_{key}", use_container_width=True):
                st.session_state.tab = key
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Extra CSS to highlight active button by index
    active_idx = [i for i,(k,_,_) in enumerate(NAV) if k == cur]
    if active_idx:
        n = active_idx[0] + 1
        st.markdown(f"""
        <style>
        #bottom-nav [data-testid="column"]:nth-child({n}) .stButton > button {{
            color: #3D2DB5 !important;
            font-weight: 700 !important;
            background: #EEECFF !important;
            border-radius: 12px !important;
        }}
        </style>""", unsafe_allow_html=True)


# ─────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────
def page_login():
    st.markdown("""
    <div style="text-align:center;padding:40px 0 20px">
        <div style="font-size:60px">🍛</div>
        <div style="font-size:24px;font-weight:700;color:#3D2DB5;margin:10px 0 4px">Rasoi Manager</div>
        <div style="color:#7B6F8A;font-size:14px">Your Indian kitchen pantry</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    hh     = st.selectbox("🏠 Household", list(HOUSEHOLDS.keys()))
    member = st.selectbox("👤 Who are you?", MEMBERS.get(hh, ["User"]))
    pwd    = st.text_input("🔑 Password", type="password", placeholder="Enter password")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sign In", use_container_width=True):
            if pwd == HOUSEHOLDS[hh]["password"]: do_login(hh, member)
            else: st.error("Wrong password.")
    with c2:
        if st.button("Guest", use_container_width=True, type="secondary"):
            do_login("👤 Guest", "Guest User")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;margin-top:14px;color:#AAA;font-size:12px">'
                'Demo: kumar123 · sharma123 · verma123 · guest</div>', unsafe_allow_html=True)


# ─────────────────────────────────────
#  HOME
# ─────────────────────────────────────
def page_home():
    pantry = st.session_state.pantry
    sync_shop()
    low = [i for i in pantry if is_low(i)]

    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card" style="background:#EEECFF">
            <div class="stat-lbl" style="color:#3D2DB5">Total items</div>
            <div class="stat-val" style="color:#3D2DB5">{len(pantry)}</div>
        </div>
        <div class="stat-card" style="background:#FFF0E8">
            <div class="stat-lbl" style="color:#B84800">Low stock</div>
            <div class="stat-val" style="color:#B84800">{len(low)}</div>
        </div>
        <div class="stat-card" style="background:#E3F8F2">
            <div class="stat-lbl" style="color:#085041">Categories</div>
            <div class="stat-val" style="color:#085041">{len(set(i["cat"] for i in pantry))}</div>
        </div>
        <div class="stat-card" style="background:#FCE4EC">
            <div class="stat-lbl" style="color:#880E4F">Shopping</div>
            <div class="stat-val" style="color:#880E4F">{len(st.session_state.shopping)}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    if low:
        st.markdown('<div class="sec-title">⚠️ Needs restocking</div>', unsafe_allow_html=True)
        for item in low[:4]:
            cat = get_cat(item["cat"])
            pct = min(100, int((item["qty"]/(item["thresh"]*4))*100))
            by  = item.get("added_by","")
            st.markdown(f"""<div class="alert-card">
                {cat['emoji']} <strong>{item['name']}</strong>
                <span class="badge badge-low">Low</span><br>
                <span style="color:#7B6F8A;font-size:12px">{item['qty']} {item['unit']} left
                {f'· {by}' if by else ''}</span>
            </div>""", unsafe_allow_html=True)
            st.progress(max(pct,4)/100)
        if len(low) > 4:
            if st.button(f"See all {len(low)} low items →", type="secondary"):
                st.session_state.tab = "pantry"; st.rerun()
    else:
        st.success("✅ Pantry is fully stocked!")

    st.markdown('<div class="sec-title">⏱️ Recently added</div>', unsafe_allow_html=True)
    for item in sorted(pantry, key=lambda x: x.get("added",""), reverse=True)[:5]:
        cat   = get_cat(item["cat"])
        color = CATEGORY_COLORS.get(item["cat"],"#F5F5F5")
        by    = item.get("added_by","")
        c1, c2 = st.columns([0.5, 5])
        with c1:
            st.markdown(f'<div class="cat-icon" style="background:{color}">{cat["emoji"]}</div>',
                        unsafe_allow_html=True)
        with c2:
            st.markdown(f"**{item['name']}** — {item['qty']} {item['unit']}")
            st.caption(f"{cat['label']}{f' · {by}' if by else ''}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Sign out", type="secondary"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()


# ─────────────────────────────────────
#  PANTRY
# ─────────────────────────────────────
def page_pantry():
    pantry = st.session_state.pantry
    search  = st.text_input("🔍 Search", placeholder="Rice, Dal, Ghee...", label_visibility="collapsed")
    opts    = ["All"] + [f"{c['emoji']} {c['label']}" for c in CATEGORIES if any(i["cat"]==c["id"] for i in pantry)]
    sel_cat = st.selectbox("Category", opts, label_visibility="collapsed")
    show_low = st.checkbox("⚠️ Low stock only")

    filtered = pantry
    if search:   filtered = [i for i in filtered if search.lower() in i["name"].lower()]
    if sel_cat != "All":
        cid = next((c["id"] for c in CATEGORIES if f"{c['emoji']} {c['label']}"==sel_cat),None)
        if cid: filtered = [i for i in filtered if i["cat"]==cid]
    if show_low: filtered = [i for i in filtered if is_low(i)]

    st.caption(f"{len(filtered)} of {len(pantry)} items")
    st.markdown("---")
    if not filtered: st.info("No items. Tap ➕ to add."); return

    for item in filtered:
        cat   = get_cat(item["cat"])
        low   = is_low(item)
        pct   = min(100, int((item["qty"]/(item["thresh"]*4))*100))
        color = CATEGORY_COLORS.get(item["cat"],"#F5F5F5")
        by    = item.get("added_by","")

        ci, cinfo, cqty = st.columns([0.55, 3, 2.2])
        with ci:
            st.markdown(f'<div class="cat-icon" style="background:{color};margin-top:6px">'
                        f'{cat["emoji"]}</div>', unsafe_allow_html=True)
        with cinfo:
            low_b = ' <span class="badge badge-low">Low</span>' if low else ""
            st.markdown(f"**{item['name']}**{low_b}", unsafe_allow_html=True)
            st.caption(f"{cat['label']}{f' · {by}' if by else ''}")
            st.progress(max(pct,3)/100)
        with cqty:
            qa, qb, qc = st.columns([1,1.4,1])
            with qa:
                if st.button("−", key=f"d_{item['id']}"):
                    item["qty"] = max(0, round(item["qty"]-1, 2))
                    sync_shop(); save_pantry(); st.rerun()
            with qb:
                st.markdown(f'<div style="text-align:center;padding-top:5px">'
                            f'<strong>{item["qty"]}</strong><br>'
                            f'<span style="font-size:10px;color:#AAA">{item["unit"]}</span></div>',
                            unsafe_allow_html=True)
            with qc:
                if st.button("+", key=f"i_{item['id']}"):
                    item["qty"] = round(item["qty"]+1, 2)
                    sync_shop(); save_pantry(); st.rerun()

        if st.button("🗑 Remove", key=f"del_{item['id']}", type="secondary"):
            st.session_state.pantry = [x for x in st.session_state.pantry if x["id"]!=item["id"]]
            save_pantry(); st.rerun()
        st.markdown('<hr style="margin:4px 0;border:none;border-top:1px solid #F0ECFF">', unsafe_allow_html=True)


# ─────────────────────────────────────
#  SHOPPING
# ─────────────────────────────────────
def page_shop():
    sync_shop()
    shop = st.session_state.shopping
    done = sum(1 for s in shop if s["checked"])
    st.caption(f"{done}/{len(shop)} done")

    name = st.text_input("Add item", placeholder="Type and press Enter", label_visibility="collapsed")
    if name:
        shop.append({"id":str(uuid.uuid4()),"name":name,"cat":"other",
                     "auto":False,"checked":False,"added_by":st.session_state.member})
        save_shopping(); st.rerun()

    c1,c2 = st.columns(2)
    with c1:
        if st.button("✓ Clear done", use_container_width=True, type="secondary"):
            st.session_state.shopping = [s for s in shop if not s["checked"]]
            save_shopping(); st.rerun()
    with c2:
        if st.button("↺ Refresh", use_container_width=True, type="secondary"):
            sync_shop(); st.rerun()

    if not shop: st.info("🛒 Empty! Low stock items appear here automatically."); return

    for title, items in [("🤖 Auto-suggested",[s for s in shop if s.get("auto")]),
                         ("✍️ Added manually", [s for s in shop if not s.get("auto")])]:
        if items:
            st.markdown(f'<div class="sec-title">{title}</div>', unsafe_allow_html=True)
            for item in items: _shop_row(item)

def _shop_row(item):
    cat = get_cat(item["cat"])
    c1,c2,c3 = st.columns([0.4,4,0.6])
    with c1:
        chk = st.checkbox("", value=item["checked"], key=f"chk_{item['id']}")
        if chk != item["checked"]: item["checked"]=chk; save_shopping(); st.rerun()
    with c2:
        s = "text-decoration:line-through;color:#BBB" if item["checked"] else "color:#1E1040"
        ab = '<span class="badge badge-low" style="font-size:10px">low</span>' if item.get("auto") else ""
        by = item.get("added_by","")
        st.markdown(f'<span style="{s};font-weight:600;font-size:14px">{item["name"]}</span> {ab}<br>'
                    f'<span style="color:#AAA;font-size:11px">{cat["emoji"]} {cat["label"]}'
                    f'{f" · {by}" if by else ""}</span>', unsafe_allow_html=True)
    with c3:
        if st.button("✕", key=f"rm_{item['id']}"):
            st.session_state.shopping=[s for s in st.session_state.shopping if s["id"]!=item["id"]]
            save_shopping(); st.rerun()
    st.markdown('<hr style="margin:4px 0;border:none;border-top:1px solid #F0ECFF">', unsafe_allow_html=True)


# ─────────────────────────────────────
#  RECIPES
# ─────────────────────────────────────
def page_recipes():
    pantry_names = {i["name"] for i in st.session_state.pantry}
    scored = []
    for r in RECIPES:
        have  = [n for n in r["needs"] if n in pantry_names]
        miss  = [n for n in r["needs"] if n not in pantry_names]
        scored.append({**r,"have":have,"miss":miss,"score":int(len(have)/len(r["needs"])*100)})
    scored.sort(key=lambda x:x["score"], reverse=True)

    search = st.text_input("🔍 Search recipes", placeholder="Dal, Upma...", label_visibility="collapsed")
    c1,c2  = st.columns(2)
    with c1: region = st.selectbox("Region",["All Regions"]+sorted({r["region"] for r in RECIPES}), label_visibility="collapsed")
    with c2: diff   = st.selectbox("Level", ["All","Easy","Medium","Hard"], label_visibility="collapsed")

    f = [r for r in scored
         if (not search or search.lower() in r["name"].lower())
         and (region=="All Regions" or r["region"]==region)
         and (diff=="All" or r["difficulty"]==diff)]

    st.markdown("---")
    for title,lst in [("✅ Ready to cook",[r for r in f if r["score"]==100]),
                      ("🛒 Almost there", [r for r in f if 50<=r["score"]<100]),
                      ("📦 Need more",    [r for r in f if r["score"]<50])]:
        if lst:
            st.markdown(f'<div class="sec-title">{title}</div>', unsafe_allow_html=True)
            for r in lst: _recipe_card(r)
    if not f: st.info("No recipes found. Add more pantry items!")

def _recipe_card(r):
    dc = {"Easy":"badge-easy","Medium":"badge-medium","Hard":"badge-hard"}.get(r["difficulty"],"badge-easy")
    with st.expander(f"{r['emoji']} **{r['name']}** — {r['score']}% · {r['time']}"):
        st.markdown(f'<span class="badge {dc}">{r["difficulty"]}</span> ⏱ {r["time"]} 👥 {r["servings"]} 📍 {r["region"]}', unsafe_allow_html=True)
        st.progress(r["score"]/100)
        have_html = " ".join(f'<span class="badge badge-have">✅ {i}</span>' for i in r["have"])
        st.markdown(have_html or "*None in pantry*", unsafe_allow_html=True)
        if r["miss"]:
            miss_html = " ".join(f'<span class="badge badge-miss">🛒 {i}</span>' for i in r["miss"])
            st.markdown(miss_html, unsafe_allow_html=True)
            if st.button("Add missing to shopping list", key=f"miss_{r['id']}"):
                for ing in r["miss"]:
                    if not any(s["name"]==ing for s in st.session_state.shopping):
                        st.session_state.shopping.append({"id":str(uuid.uuid4()),"name":ing,
                            "cat":"other","auto":False,"checked":False,"added_by":st.session_state.member})
                save_shopping(); st.success(f"Added {len(r['miss'])} items!")
        st.markdown("**Steps:**")
        for i,step in enumerate(r["steps"],1): st.markdown(f"**{i}.** {step}")


# ─────────────────────────────────────
#  ADD ITEM
# ─────────────────────────────────────
def page_add():
    pantry_names = {i["name"] for i in st.session_state.pantry}
    available    = [s for s in INDIAN_STAPLES if s["name"] not in pantry_names]

    st.markdown('<div class="sec-title">⚡ Quick pick</div>', unsafe_allow_html=True)
    qp = st.selectbox("Staple", ["— choose —"]+[s["name"] for s in available[:40]], label_visibility="collapsed")
    qd = next((s for s in available if s["name"]==qp), None) if qp!="— choose —" else None

    st.markdown('<div class="sec-title">📝 Item details</div>', unsafe_allow_html=True)
    name = st.text_input("Item name *", value=qd["name"] if qd else "", placeholder="e.g. Basmati Rice")
    cat_labels = [f"{c['emoji']} {c['label']}" for c in CATEGORIES]
    def_cat    = next((i for i,c in enumerate(CATEGORIES) if c["id"]==qd["cat"]),0) if qd else 0
    sel_cat    = st.selectbox("Category", cat_labels, index=def_cat)
    cat_id     = CATEGORIES[cat_labels.index(sel_cat)]["id"]

    c1,c2 = st.columns(2)
    with c1:
        qty  = st.number_input("Quantity", min_value=0.0, value=float(qd["qty"]) if qd else 1.0, step=0.5)
        unit = st.selectbox("Unit", UNITS, index=UNITS.index(qd["unit"]) if qd and qd["unit"] in UNITS else 0)
    with c2:
        thresh = st.number_input("Alert when below", min_value=0.0, value=float(qd["thresh"]) if qd else 1.0, step=0.5)

    if st.button("✅ Add to Pantry", use_container_width=True):
        if not name.strip(): st.error("Enter an item name.")
        else:
            st.session_state.pantry.insert(0,{"id":str(uuid.uuid4()),"name":name.strip(),
                "cat":cat_id,"qty":round(qty,2),"unit":unit,"thresh":round(thresh,2),
                "added":datetime.now().isoformat(),"added_by":st.session_state.member})
            sync_shop(); save_pantry()
            st.success(f"✅ **{name}** added!"); st.balloons()

    st.markdown('<div class="sec-title">📋 Bulk add</div>', unsafe_allow_html=True)
    bulk = st.multiselect("Pick staples", [s["name"] for s in available], placeholder="Select multiple...")
    if bulk and st.button(f"➕ Add {len(bulk)} items", use_container_width=True):
        for sname in bulk:
            s = next((x for x in available if x["name"]==sname),None)
            if s:
                st.session_state.pantry.insert(0,{**s,"id":str(uuid.uuid4()),
                    "added":datetime.now().isoformat(),"added_by":st.session_state.member})
        sync_shop(); save_pantry()
        st.success(f"✅ Added {len(bulk)} items!"); st.rerun()


# ─────────────────────────────────────
#  MAIN
# ─────────────────────────────────────
def main():
    if not st.session_state.get("logged_in"):
        page_login()
        return

    top_bar()

    tab = st.session_state.get("tab","home")
    if   tab == "home":    page_home()
    elif tab == "pantry":  page_pantry()
    elif tab == "shop":    page_shop()
    elif tab == "recipes": page_recipes()
    elif tab == "add":     page_add()

    bottom_nav()

if __name__ == "__main__":
    main()
