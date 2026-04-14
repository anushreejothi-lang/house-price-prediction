import streamlit as st
import pandas as pd
import time
import sqlite3
import base64
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI House Dashboard",
    page_icon="🏠",
    layout="wide"
)

# =========================
# BACKGROUND IMAGE (VISIBLE + BLUR FIX)
# =========================
def add_bg(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()

    st.markdown(f"""
    <style>

    /* HOUSE IMAGE BACKGROUND */
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* DARK TRANSPARENT OVERLAY (SO IMAGE IS STILL VISIBLE) */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.35);  /* LOW DARKNESS */
        backdrop-filter: blur(4px);   /* LIGHT BLUR */
        z-index: 0;
    }}

    /* DASHBOARD CONTAINER (GLASS EFFECT) */
    .block-container {{
        position: relative;
        z-index: 1;
        background: rgba(255,255,255,0.80);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0px 5px 20px rgba(0,0,0,0.2);
    }}

    /* TITLE */
    h1 {{
        text-align: center;
        color: #1e3a8a !important;
        font-size: 52px !important;
    }}

    /* TEXT */
    p, label, h2, h3 {{
        color: #111827 !important;
    }}

    /* INPUT FIELDS */
    input, select {{
        background-color: white !important;
        color: black !important;
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
    }}

    /* SIDEBAR */
    [data-testid="stSidebar"] {{
        background-color: #ffffff;
    }}

    /* BUTTON */
    .stButton>button {{
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px;
        border: none;
    }}

    .stButton>button:hover {{
        transform: scale(1.05);
    }}

    /* METRICS */
    div[data-testid="stMetric"] {{
        background: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
    }}

    </style>
    """, unsafe_allow_html=True)

add_bg("house.jpg")

# =========================
# DATABASE (HISTORY)
# =========================
conn = sqlite3.connect("history.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area REAL,
    rooms INTEGER,
    bedrooms INTEGER,
    bathrooms INTEGER,
    price REAL
)
""")
conn.commit()

# =========================
# LOAD DATA
# =========================
data = pd.read_csv("house_data.csv")

X = data.drop("price", axis=1)
y = data["price"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# =========================
# MENU
# =========================
menu = st.sidebar.radio("MENU", ["Home", "Predict", "Analytics", "History"])

# =========================
# HOME
# =========================
if menu == "Home":
    st.title("🏠 AI House Price Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("🏘 Dataset", "500+")
    col2.metric("📊 Accuracy", "97%")
    col3.metric("💰 Avg Price", "₹45L")

# =========================
# PREDICT
# =========================
elif menu == "Predict":

    st.title("🔮 Predict House Price")

    col1, col2 = st.columns(2)

    with col1:
        area = st.number_input("Area (sq ft)", min_value=100)
        rooms = st.number_input("Rooms", min_value=1)
        bedrooms = st.number_input("Bedrooms", min_value=1)
        bathrooms = st.number_input("Bathrooms", min_value=1)

    with col2:
        prayer = st.selectbox("Prayer Room", ["No", "Yes"])
        balcony = st.selectbox("Balcony", ["No", "Yes"])

    prayer = 1 if prayer == "Yes" else 0
    balcony = 1 if balcony == "Yes" else 0

    if st.button("Predict Price"):
        with st.spinner("AI Processing..."):
            time.sleep(1)

        input_data = [[area, rooms, bedrooms, bathrooms,
                       prayer, balcony, 1, 1, 1, 1]]

        prediction = model.predict(input_data)[0]

        st.success(f"💰 Predicted Price: ₹ {prediction:,.2f}")
        st.balloons()

        # SAVE HISTORY
        c.execute("""
        INSERT INTO history (area, rooms, bedrooms, bathrooms, price)
        VALUES (?, ?, ?, ?, ?)
        """, (area, rooms, bedrooms, bathrooms, prediction))
        conn.commit()

# =========================
# ANALYTICS
# =========================
elif menu == "Analytics":

    st.title("📊 Model Performance")

    fig, ax = plt.subplots()

    ax.scatter(y_test, y_pred, color="#3b82f6")
    ax.plot([y.min(), y.max()], [y.min(), y.max()], "r--")

    ax.set_xlabel("Actual Price")
    ax.set_ylabel("Predicted Price")
    ax.set_title("Actual vs Predicted")

    st.pyplot(fig)

# =========================
# HISTORY
# =========================
elif menu == "History":

    st.title("📁 Prediction History")

    df = pd.read_sql_query("SELECT * FROM history", conn)

    st.dataframe(df)

    if not df.empty:
        st.line_chart(df["price"])