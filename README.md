# 🍛 Rasoi Manager — Streamlit Web App

A fully functional Indian kitchen pantry manager built with Python + Streamlit.
Runs in your browser. No phone, no Node.js, no Android Studio needed.

---

## 🚀 Setup (3 steps)

### Step 1 — Install Python
Download from https://www.python.org/downloads/ (version 3.9 or higher)
Make sure to check ✅ "Add Python to PATH" during install.

### Step 2 — Install libraries
Open VS Code terminal, navigate to this folder and run:
```bash
pip install -r requirements.txt
```

### Step 3 — Run the app
```bash
streamlit run app.py
```
Browser opens automatically at http://localhost:8501

---

## 📁 File Structure

```
rasoi_streamlit/
├── app.py          ← Main app (all screens & logic)
├── data.py         ← ✏️ Edit ingredients & recipes here
├── requirements.txt
└── README.md
```

---

## ✏️ How to Customize

### Add a new recipe
Open `data.py`, add to the `RECIPES` list:
```python
{
    "id": "r13",
    "name": "Pav Bhaji",
    "emoji": "🫓",
    "difficulty": "Easy",
    "time": "30 min",
    "servings": 4,
    "region": "Maharashtrian",
    "needs": ["Potatoes", "Onions", "Tomatoes", "Butter", "Garam Masala"],
    "steps": [
        "Boil and mash potatoes and mixed vegetables.",
        "Sauté onions and tomatoes in butter with pav bhaji masala.",
        "Mix in mashed vegetables, cook till thick.",
        "Toast pav with butter, serve with bhaji.",
    ],
},
```

### Change colors
Open `app.py`, find the `<style>` block near the top.
Change `#3D2DB5` (indigo) to any color you like.

### Add new ingredients
Open `data.py`, add to `INDIAN_STAPLES`:
```python
{"name": "Kokum", "cat": "condiments", "qty": 100.0, "unit": "g", "thresh": 30.0},
```

---

## 📌 Notes
- Data is stored in session (resets on browser refresh — this is a prototype)
- To persist data across sessions, integrate SQLite or a JSON file save/load
- To deploy online, use Streamlit Community Cloud (free): https://streamlit.io/cloud
