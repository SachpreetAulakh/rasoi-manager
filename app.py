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

# ─────────────────────────────────────────────────────────────
#  MASTER CSS
#  Key fix: html/body height 100%, overflow hidden on body,
#  only the #main-content div scrolls. Nav is truly fixed.
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html {
    height: 100%;
    /* Disable pull-to-refresh on mobile browsers */
    overscroll-behavior-y: contain;
}

body {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: #F7F3FF;
    height: 100%;
    overscroll-behavior-y: contain;
    overflow: hidden;          /* body itself never scrolls */
}

/* ── Hide all Streamlit chrome ── */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarToggle"],
.st-emotion-cache-1rtdyuf,
.st-emotion-cache-pkbazv,
#MainMenu, footer, header,
.stDeployButton { display: none !important; }

/* ── Streamlit's root wrappers — let them fill height ── */
.stApp, [data-testid="stAppViewContainer"] {
    height: 100dvh !important;
    overflow: hidden !important;
    background: #F7F3FF !important;
}

[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main {
    height: 100% !important;
    overflow: hidden !important;
    padding: 0 !important;
}

/* ── Block container: fill space, no scroll ── */
.main .block-container {
    padding: 0 !important;
    margin: 0 auto !important;
    max-width: 480px !important;
    height: 100dvh !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}

/* ── TOP BAR — fixed at top, never scrolls ── */
#top-bar {
    flex-shrink: 0;
    background: #3D2DB5;
    padding: 14px 16px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 100;
}
.tb-title { color: #fff; font-size: 18px; font-weight: 700; }
.tb-sub   { color: rgba(255,255,255,.7); font-size: 11px; margin-top: 2px; }
.tb-user  {
    background: rgba(255,255,255,.2); border-radius: 20px;
    padding: 4px 12px; color: #fff; font-size: 12px; font-weight: 500;
}

/* ── SCROLL AREA — only this div scrolls ── */
#scroll-area {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
    padding: 14px 12px 12px;
    overscroll-behavior-y: contain;  /* prevent pull-to-refresh inside scroll area */
}

/* ── BOTTOM NAV — fixed at bottom, never scrolls ── */
#bottom-nav {
    flex-shrink: 0;
    background: #fff;
    border-top: 1.5px solid rgba(61,45,181,.12);
    box-shadow: 0 -3px 16px rgba(61,45,181,.1);
    display: flex;
    padding: 6px 4px 10px;
    z-index: 100;
}
.nav-btn {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 5px 2px 3px;
    border-radius: 10px;
    transition: background .15s;
    text-decoration: none;
}
.nav-btn:hover  { background: #F0ECFF; }
.nav-btn.active { background: #EEECFF; }
.nav-icon  { font-size: 22px; line-height: 1; }
.nav-label { font-size: 10px; font-weight: 500; color: #AAA0BB; }
.nav-btn.active .nav-label { color: #3D2DB5; font-weight: 700; }
.nav-dot   { width: 4px; height: 4px; border-radius: 50%; background: #3D2DB5; margin-top: 1px; }

/* ── Streamlit widget container — remove its own padding ── */
[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* ── Stat grid ── */
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
.stat-card { border-radius: 14px; padding: 13px 14px; border: 1px solid rgba(100,60,180,.12); }
.s-lbl { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing:.06em; margin-bottom:3px; }
.s-val { font-size: 26px; font-weight: 700; line-height: 1.1; }

/* ── Section title ── */
.sec-title {
    font-size: 14px; font-weight: 700; color: #1E1040;
    margin: 14px 0 8px; padding-bottom: 4px;
    border-bottom: 2px solid #EEECFF;
}

/* ── Alert & item cards ── */
.alert-card {
    background: #FFF0E8; border: 1px solid rgba(232,96,10,.22);
    border-radius: 12px; padding: 10px 12px; margin-bottom: 7px;
    font-size: 13px;
}
.item-row {
    background: #fff; border: 1px solid rgba(100,60,180,.11);
    border-radius: 12px; padding: 10px 12px; margin-bottom: 7px;
    display: flex; align-items: center; gap: 10px;
}
.item-row.low { border-color: rgba(232,96,10,.28); }

/* ── Cat icon ── */
.cicon {
    width: 40px; height: 40px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 19px; flex-shrink: 0;
}

/* ── Badges ── */
.badge { display:inline-block; padding:1px 7px; border-radius:5px; font-size:10px; font-weight:700; }
.bl  { background:#FFF0E8; color:#B84800; }
.be  { background:#E3F8F2; color:#085041; }
.bm  { background:#FFF8E1; color:#7A4800; }
.bh  { background:#FCE4EC; color:#880E4F; }
.bhv { background:#EEECFF; color:#3D2DB5; }
.bms { background:#FFF0E8; color:#B84800; }

/* ── Buttons ── */
.stButton > button {
    background: #3D2DB5 !important; color: #fff !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 13px !important;
    padding: 8px 12px !important;
}
.stButton > button[kind="secondary"] {
    background: #fff !important; color: #3D2DB5 !important;
    border: 1.5px solid rgba(61,45,181,.28) !important;
}
.stButton > button:hover { opacity: .88 !important; }

/* ── Inputs ── */
.stTextInput input, .stNumberInput input, .stSelectbox > div > div {
    border-color: rgba(100,60,180,.22) !important;
    border-radius: 9px !important; font-size: 13px !important;
}
.stProgress > div > div { background: #3D2DB5 !important; }
.streamlit-expanderHeader {
    background: #F0ECFF !important; border-radius: 9px !important; font-weight: 600 !important;
}

/* ── Login card ── */
.login-card {
    background: #fff; border-radius: 18px; padding: 24px 20px;
    border: 1px solid rgba(100,60,180,.13); margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── JavaScript: disable pull-to-refresh + localStorage auto-login ──
st.markdown("""
<script>
// Disable pull-to-refresh gesture
document.addEventListener('touchstart', function(e) {}, {passive: true});
let lastY = 0;
document.addEventListener('touchmove', function(e) {
    const y = e.touches[0].clientY;
    const el = document.querySelector('#scroll-area');
    if (el && el.scrollTop === 0 && y > lastY) {
        e.preventDefault();
    }
    lastY = y;
}, {passive: false});
</script>
""", unsafe_allow_html=True)


# ──────────────────────────────────────
#  CONFIG  ✏️ Edit to add households
# ──────────────────────────────────────
HOUSEHOLDS = {
    "🏠 Aulakh Family":  {"password": "Aulakh123"},
    "🏡 Khangura Family": {"password": "Khangura123"},
    }
MEMBERS = {
    "🏠 Aulakh Family":  ["Sukh", "Sach"],
    "🏡 Khangura Family": ["Manpreet", "Honey"],
  }
NAV = [
    ("home",    "🏠", "Home"),
    ("pantry",  "📦", "Pantry"),
    ("shop",    "🛒", "Shop"),
    ("recipes", "🍽️", "Recipes"),
    ("add",     "➕", "Add"),
]
PAGE_META = {
    "home":    ("🏠", "Dashboard",  "Your kitchen at a glance"),
    "pantry":  ("📦", "Pantry",     "Manage your stock"),
    "shop":    ("🛒", "Shopping",   "Your shopping list"),
    "recipes": ("🍽️", "Recipes",    "What can you cook?"),
    "add":     ("➕", "Add Item",   "Add to pantry"),
}


# ──────────────────────────────────────
#  DATA HELPERS
# ──────────────────────────────────────
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

def save_pantry():   save_j(dpath(st.session_state.hh, "pantry"),   st.session_state.pantry)
def save_shopping(): save_j(dpath(st.session_state.hh, "shopping"), st.session_state.shopping)

def get_cat(cid): return next((c for c in CATEGORIES if c["id"]==cid), {"label":cid,"emoji":"📦"})
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
    st.session_state.shopping = [
        s for s in shop if not s.get("auto") or s.get("source_id") in low_ids]
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
    st.session_state.logged_in = True
    st.session_state.hh        = hh
    st.session_state.member    = member
    st.session_state.tab       = "home"
    pantry = load_j(dpath(hh,"pantry"), [])
    if not pantry:
        pantry = seed(member)
        save_j(dpath(hh,"pantry"), pantry)
    st.session_state.pantry   = pantry
    st.session_state.shopping = load_j(dpath(hh,"shopping"), [])
    st.rerun()


# ──────────────────────────────────────
#  TOP BAR HTML
# ──────────────────────────────────────
def render_top_bar():
    tab  = st.session_state.get("tab","home")
    icon, title, sub = PAGE_META.get(tab, ("🍛","Rasoi",""))
    member = st.session_state.get("member","")
    st.markdown(f"""
    <div id="top-bar">
      <div>
        <div class="tb-title">{icon} {title}</div>
        <div class="tb-sub">{sub}</div>
      </div>
      <div class="tb-user">👤 {member}</div>
    </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────
#  BOTTOM NAV  — HTML buttons + hidden
#  Streamlit buttons for actual routing
# ──────────────────────────────────────
def render_bottom_nav():
    cur = st.session_state.get("tab","home")

    # Build the visible HTML nav
    nav_items = ""
    for key, icon, label in NAV:
        active = "active" if cur == key else ""
        dot    = '<div class="nav-dot"></div>' if cur == key else ""
        nav_items += f"""
        <div class="nav-btn {active}" onclick="document.getElementById('navbtn-{key}').click()">
            <span class="nav-icon">{icon}</span>
            <span class="nav-label">{label}</span>
            {dot}
        </div>"""

    st.markdown(f'<div id="bottom-nav">{nav_items}</div>', unsafe_allow_html=True)

    # Hidden Streamlit buttons — triggered by the HTML nav onclick
    btn_css = """
    <style>
    div[data-testid="stHorizontalBlock"].nav-hidden-row {
        position: absolute !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 1px !important;
        overflow: hidden !important;
    }
    </style>"""
    st.markdown(btn_css, unsafe_allow_html=True)

    cols = st.columns(len(NAV))
    for i, (key, icon, label) in enumerate(NAV):
        with cols[i]:
            # Give each button an id so the HTML nav can click it
            clicked = st.button(label, key=f"navbtn_{key}", use_container_width=True)
            if clicked:
                st.session_state.tab = key
                st.rerun()

    # Inject IDs into the hidden buttons via JS
    st.markdown("""
    <script>
    (function() {
        const keys = """ + str([k for k,_,_ in NAV]) + """;
        keys.forEach(function(key) {
            const btns = Array.from(document.querySelectorAll('button'));
            const btn  = btns.find(b => b.innerText.trim() === key ||
                                        b.getAttribute('data-testid') === 'navbtn-'+key);
            if (btn) btn.id = 'navbtn-' + key;
        });
    })();
    </script>""", unsafe_allow_html=True)


# ──────────────────────────────────────
#  OPEN / CLOSE scroll area wrappers
# ──────────────────────────────────────
def open_scroll():
    st.markdown('<div id="scroll-area">', unsafe_allow_html=True)

def close_scroll():
    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────
#  LOGIN
# ──────────────────────────────────────
def page_login():
    # Auto-login check via localStorage
    st.markdown("""
    <script>
    (function() {
        try {
            const saved = localStorage.getItem('rasoi_session');
            if (saved) {
                const sess = JSON.parse(saved);
                const hhInput   = document.querySelector('select');
                const memberSel = document.querySelectorAll('select')[1];
                const pwdInput  = document.querySelector('input[type=password]');
                if (hhInput && sess.hh)     hhInput.value   = sess.hh;
                if (memberSel && sess.member) memberSel.value = sess.member;
                if (pwdInput && sess.pwd)   pwdInput.value  = sess.pwd;
            }
        } catch(e) {}
    })();
    </script>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:36px 0 18px">
        <div style="font-size:56px">🍛</div>
        <div style="font-size:22px;font-weight:700;color:#3D2DB5;margin:8px 0 3px">Rasoi Manager</div>
        <div style="color:#7B6F8A;font-size:13px">Your Indian kitchen pantry</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    hh     = st.selectbox("🏠 Household", list(HOUSEHOLDS.keys()))
    member = st.selectbox("👤 Who are you?", MEMBERS.get(hh, ["User"]))
    pwd    = st.text_input("🔑 Password", type="password", placeholder="Enter password")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sign In", use_container_width=True):
            if pwd == HOUSEHOLDS[hh]["password"]:
                # Save to localStorage so refresh doesn't log out
                st.markdown(f"""
                <script>
                localStorage.setItem('rasoi_session', JSON.stringify({{
                    hh: '{hh}', member: '{member}', pwd: '{pwd}'
                }}));
                </script>""", unsafe_allow_html=True)
                do_login(hh, member)
            else:
                st.error("Wrong password.")
    with c2:
        if st.button("Guest", use_container_width=True, type="secondary"):
            do_login("👤 Guest", "Guest User")

    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("Demo: kumar123 · sharma123 · verma123 · guest")


# ──────────────────────────────────────
#  HOME
# ──────────────────────────────────────
def page_home():
    pantry = st.session_state.pantry
    sync_shop()
    low = [i for i in pantry if is_low(i)]

    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-card" style="background:#EEECFF">
        <div class="s-lbl" style="color:#3D2DB5">Total items</div>
        <div class="s-val" style="color:#3D2DB5">{len(pantry)}</div>
      </div>
      <div class="stat-card" style="background:#FFF0E8">
        <div class="s-lbl" style="color:#B84800">Low stock</div>
        <div class="s-val" style="color:#B84800">{len(low)}</div>
      </div>
      <div class="stat-card" style="background:#E3F8F2">
        <div class="s-lbl" style="color:#085041">Categories</div>
        <div class="s-val" style="color:#085041">{len(set(i["cat"] for i in pantry))}</div>
      </div>
      <div class="stat-card" style="background:#FCE4EC">
        <div class="s-lbl" style="color:#880E4F">Shopping</div>
        <div class="s-val" style="color:#880E4F">{len(st.session_state.shopping)}</div>
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
                <span class="badge bl">Low</span><br>
                <span style="color:#7B6F8A;font-size:11px">{item['qty']} {item['unit']} left
                {f'· {by}' if by else ''}</span>
            </div>""", unsafe_allow_html=True)
            st.progress(max(pct,4)/100)
        if len(low)>4:
            if st.button(f"See all {len(low)} →", type="secondary"):
                st.session_state.tab="pantry"; st.rerun()
    else:
        st.success("✅ Pantry is fully stocked!")

    st.markdown('<div class="sec-title">⏱️ Recently added</div>', unsafe_allow_html=True)
    for item in sorted(pantry, key=lambda x: x.get("added",""), reverse=True)[:5]:
        cat   = get_cat(item["cat"])
        color = CATEGORY_COLORS.get(item["cat"],"#F5F5F5")
        by    = item.get("added_by","")
        c1, c2 = st.columns([0.5,5])
        with c1:
            st.markdown(f'<div class="cicon" style="background:{color}">{cat["emoji"]}</div>',
                        unsafe_allow_html=True)
        with c2:
            st.markdown(f"**{item['name']}** — {item['qty']} {item['unit']}")
            st.caption(f"{cat['label']}{f' · {by}' if by else ''}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Sign out", type="secondary"):
        st.markdown("<script>localStorage.removeItem('rasoi_session');</script>",
                    unsafe_allow_html=True)
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()


# ──────────────────────────────────────
#  PANTRY
# ──────────────────────────────────────
def page_pantry():
    pantry = st.session_state.pantry
    search  = st.text_input("🔍 Search", placeholder="Rice, Dal, Ghee...", label_visibility="collapsed")
    opts    = ["All"]+[f"{c['emoji']} {c['label']}" for c in CATEGORIES if any(i["cat"]==c["id"] for i in pantry)]
    sel_cat = st.selectbox("Category", opts, label_visibility="collapsed")
    show_low = st.checkbox("⚠️ Low stock only")

    filtered = pantry
    if search:    filtered = [i for i in filtered if search.lower() in i["name"].lower()]
    if sel_cat!="All":
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

        ci, cinfo, cqty = st.columns([0.5, 3, 2.2])
        with ci:
            st.markdown(f'<div class="cicon" style="background:{color};margin-top:5px">'
                        f'{cat["emoji"]}</div>', unsafe_allow_html=True)
        with cinfo:
            low_b = ' <span class="badge bl">Low</span>' if low else ""
            st.markdown(f"**{item['name']}**{low_b}", unsafe_allow_html=True)
            st.caption(f"{cat['label']}{f' · {by}' if by else ''}")
            st.progress(max(pct,3)/100)
        with cqty:
            qa,qb,qc = st.columns([1,1.4,1])
            with qa:
                if st.button("−", key=f"d_{item['id']}"):
                    item["qty"]=max(0,round(item["qty"]-1,2))
                    sync_shop(); save_pantry(); st.rerun()
            with qb:
                st.markdown(f'<div style="text-align:center;padding-top:4px">'
                            f'<strong>{item["qty"]}</strong><br>'
                            f'<span style="font-size:10px;color:#AAA">{item["unit"]}</span></div>',
                            unsafe_allow_html=True)
            with qc:
                if st.button("+", key=f"i_{item['id']}"):
                    item["qty"]=round(item["qty"]+1,2)
                    sync_shop(); save_pantry(); st.rerun()

        if st.button("🗑 Remove", key=f"del_{item['id']}", type="secondary"):
            st.session_state.pantry=[x for x in st.session_state.pantry if x["id"]!=item["id"]]
            save_pantry(); st.rerun()
        st.markdown('<hr style="margin:4px 0;border:none;border-top:1px solid #F0ECFF">',
                    unsafe_allow_html=True)


# ──────────────────────────────────────
#  SHOPPING
# ──────────────────────────────────────
def page_shop():
    sync_shop()
    shop = st.session_state.shopping
    done = sum(1 for s in shop if s["checked"])
    st.caption(f"{done}/{len(shop)} done")

    name = st.text_input("Add item", placeholder="Type and press Enter",
                         label_visibility="collapsed")
    if name:
        shop.append({"id":str(uuid.uuid4()),"name":name,"cat":"other",
                     "auto":False,"checked":False,"added_by":st.session_state.member})
        save_shopping(); st.rerun()

    c1,c2 = st.columns(2)
    with c1:
        if st.button("✓ Clear done", use_container_width=True, type="secondary"):
            st.session_state.shopping=[s for s in shop if not s["checked"]]
            save_shopping(); st.rerun()
    with c2:
        if st.button("↺ Refresh", use_container_width=True, type="secondary"):
            sync_shop(); st.rerun()

    if not shop: st.info("🛒 Empty! Low stock items appear automatically."); return

    for title, items in [("🤖 Auto-suggested",[s for s in shop if s.get("auto")]),
                         ("✍️ Added manually", [s for s in shop if not s.get("auto")])]:
        if items:
            st.markdown(f'<div class="sec-title">{title}</div>', unsafe_allow_html=True)
            for item in items: _shop_row(item)

def _shop_row(item):
    cat=get_cat(item["cat"])
    c1,c2,c3=st.columns([0.4,4,0.6])
    with c1:
        chk=st.checkbox("",value=item["checked"],key=f"chk_{item['id']}")
        if chk!=item["checked"]: item["checked"]=chk; save_shopping(); st.rerun()
    with c2:
        s="text-decoration:line-through;color:#BBB" if item["checked"] else "color:#1E1040"
        ab='<span class="badge bl" style="font-size:9px">low</span>' if item.get("auto") else ""
        by=item.get("added_by","")
        st.markdown(f'<span style="{s};font-weight:600;font-size:13px">{item["name"]}</span> {ab}<br>'
                    f'<span style="color:#AAA;font-size:11px">{cat["emoji"]} {cat["label"]}'
                    f'{f" · {by}" if by else ""}</span>', unsafe_allow_html=True)
    with c3:
        if st.button("✕",key=f"rm_{item['id']}"):
            st.session_state.shopping=[s for s in st.session_state.shopping if s["id"]!=item["id"]]
            save_shopping(); st.rerun()
    st.markdown('<hr style="margin:3px 0;border:none;border-top:1px solid #F0ECFF">',
                unsafe_allow_html=True)


# ──────────────────────────────────────
#  RECIPES
# ──────────────────────────────────────
def page_recipes():
    pantry_names={i["name"] for i in st.session_state.pantry}
    scored=[]
    for r in RECIPES:
        have=[n for n in r["needs"] if n in pantry_names]
        miss=[n for n in r["needs"] if n not in pantry_names]
        scored.append({**r,"have":have,"miss":miss,"score":int(len(have)/len(r["needs"])*100)})
    scored.sort(key=lambda x:x["score"],reverse=True)

    search=st.text_input("🔍 Search",placeholder="Dal, Upma...",label_visibility="collapsed")
    c1,c2=st.columns(2)
    with c1: region=st.selectbox("Region",["All"]+sorted({r["region"] for r in RECIPES}),label_visibility="collapsed")
    with c2: diff=st.selectbox("Level",["All","Easy","Medium","Hard"],label_visibility="collapsed")

    f=[r for r in scored
       if (not search or search.lower() in r["name"].lower())
       and (region=="All" or r["region"]==region)
       and (diff=="All" or r["difficulty"]==diff)]

    st.markdown("---")
    for title,lst in [("✅ Ready to cook",[r for r in f if r["score"]==100]),
                      ("🛒 Almost there", [r for r in f if 50<=r["score"]<100]),
                      ("📦 Need more",    [r for r in f if r["score"]<50])]:
        if lst:
            st.markdown(f'<div class="sec-title">{title}</div>',unsafe_allow_html=True)
            for r in lst: _recipe_card(r)
    if not f: st.info("No recipes found. Add more pantry items!")

def _recipe_card(r):
    dc={"Easy":"be","Medium":"bm","Hard":"bh"}.get(r["difficulty"],"be")
    with st.expander(f"{r['emoji']} **{r['name']}** — {r['score']}% · {r['time']}"):
        st.markdown(f'<span class="badge {dc}">{r["difficulty"]}</span> ⏱ {r["time"]} 👥 {r["servings"]} 📍 {r["region"]}',unsafe_allow_html=True)
        st.progress(r["score"]/100)
        have_html=" ".join(f'<span class="badge bhv">✅ {i}</span>' for i in r["have"])
        st.markdown(have_html or "*None in pantry*",unsafe_allow_html=True)
        if r["miss"]:
            miss_html=" ".join(f'<span class="badge bms">🛒 {i}</span>' for i in r["miss"])
            st.markdown(miss_html,unsafe_allow_html=True)
            if st.button("Add missing to list",key=f"miss_{r['id']}"):
                for ing in r["miss"]:
                    if not any(s["name"]==ing for s in st.session_state.shopping):
                        st.session_state.shopping.append({"id":str(uuid.uuid4()),"name":ing,
                            "cat":"other","auto":False,"checked":False,"added_by":st.session_state.member})
                save_shopping(); st.success(f"Added {len(r['miss'])} items!")
        st.markdown("**Steps:**")
        for i,step in enumerate(r["steps"],1): st.markdown(f"**{i}.** {step}")


# ──────────────────────────────────────
#  ADD ITEM
# ──────────────────────────────────────
def page_add():
    pantry_names={i["name"] for i in st.session_state.pantry}
    available=[s for s in INDIAN_STAPLES if s["name"] not in pantry_names]

    st.markdown('<div class="sec-title">⚡ Quick pick</div>',unsafe_allow_html=True)
    qp=st.selectbox("Staple",["— choose —"]+[s["name"] for s in available[:40]],label_visibility="collapsed")
    qd=next((s for s in available if s["name"]==qp),None) if qp!="— choose —" else None

    st.markdown('<div class="sec-title">📝 Details</div>',unsafe_allow_html=True)
    name=st.text_input("Item name *",value=qd["name"] if qd else "",placeholder="e.g. Basmati Rice")
    cat_labels=[f"{c['emoji']} {c['label']}" for c in CATEGORIES]
    def_cat=next((i for i,c in enumerate(CATEGORIES) if c["id"]==qd["cat"]),0) if qd else 0
    sel_cat=st.selectbox("Category",cat_labels,index=def_cat)
    cat_id=CATEGORIES[cat_labels.index(sel_cat)]["id"]

    c1,c2=st.columns(2)
    with c1:
        qty=st.number_input("Quantity",min_value=0.0,value=float(qd["qty"]) if qd else 1.0,step=0.5)
        unit=st.selectbox("Unit",UNITS,index=UNITS.index(qd["unit"]) if qd and qd["unit"] in UNITS else 0)
    with c2:
        thresh=st.number_input("Alert below",min_value=0.0,value=float(qd["thresh"]) if qd else 1.0,step=0.5)

    if st.button("✅ Add to Pantry",use_container_width=True):
        if not name.strip(): st.error("Enter a name.")
        else:
            st.session_state.pantry.insert(0,{"id":str(uuid.uuid4()),"name":name.strip(),
                "cat":cat_id,"qty":round(qty,2),"unit":unit,"thresh":round(thresh,2),
                "added":datetime.now().isoformat(),"added_by":st.session_state.member})
            sync_shop(); save_pantry()
            st.success(f"✅ {name} added!"); st.balloons()

    st.markdown('<div class="sec-title">📋 Bulk add</div>',unsafe_allow_html=True)
    bulk=st.multiselect("Pick staples",[s["name"] for s in available],placeholder="Select multiple...")
    if bulk and st.button(f"➕ Add {len(bulk)} items",use_container_width=True):
        for sname in bulk:
            s=next((x for x in available if x["name"]==sname),None)
            if s:
                st.session_state.pantry.insert(0,{**s,"id":str(uuid.uuid4()),
                    "added":datetime.now().isoformat(),"added_by":st.session_state.member})
        sync_shop(); save_pantry()
        st.success(f"✅ Added {len(bulk)} items!"); st.rerun()


# ──────────────────────────────────────
#  MAIN
# ──────────────────────────────────────
def main():
    if not st.session_state.get("logged_in"):
        page_login()
        return

    render_top_bar()
    open_scroll()

    tab = st.session_state.get("tab","home")
    if   tab=="home":    page_home()
    elif tab=="pantry":  page_pantry()
    elif tab=="shop":    page_shop()
    elif tab=="recipes": page_recipes()
    elif tab=="add":     page_add()

    close_scroll()
    render_bottom_nav()

if __name__ == "__main__":
    main()
