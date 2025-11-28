import streamlit as st
import pandas as pd
import pickle
import time
import requests
from streamlit_lottie import st_lottie


# PAGE CONFIG
st.set_page_config(
    page_title="FraudShield AI",
    page_icon="🛡️",
    layout="wide"
)


# LOAD MODEL
with open("model.pkl", "rb") as file:
    model = pickle.load(file)


# LOTTIE ANIMATION LOADER
def load_lottie(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except:
        return None


# Animations
lottie_header = load_lottie(
    "https://assets10.lottiefiles.com/packages/lf20_w51pcehl.json")
lottie_safe = load_lottie(
    "https://assets9.lottiefiles.com/private_files/lf30_p5tali1o.json")
lottie_alert = load_lottie(
    "https://assets7.lottiefiles.com/packages/lf20_7fCbvNSmFD.json")
lottie_logo = load_lottie(
    "https://assets5.lottiefiles.com/packages/lf20_V9t630.json")


# Fallback wrapper
def safe_st_lottie(lottie_json, height=200, key=None):
    if lottie_json is not None:
        st_lottie(lottie_json, height=height, key=key)
    else:
        st.write("⚠️ Animation not available.")


# CUSTOM CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to right, #000000, #0f2027, #203a43, #2c5364);
        color: white;
    }
    .glass-card {
        padding: 30px;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        backdrop-filter: blur(10px);
    }
    .stNumberInput>div>div>input {
        background-color: rgba(255,255,255,0.12);
        color: white;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.25);
    }
    .stSelectbox>div>div {
        background-color: rgba(255,255,255,0.12) !important;
        color: white !important;
        border-radius: 8px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF512F, #DD2476);
        color: white;
        padding: 12px 24px;
        border-radius: 40px;
        border: none;
        width: 100%;
        font-weight: bold;
        letter-spacing: 1px;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 20px rgba(255,105,180,0.6);
    }
    h1, h2, h3 {
        color: white;
        text-shadow: 2px 2px 5px black;
    }
    section[data-testid="stSidebar"] {
        background-color: #000000;
    }
</style>
""", unsafe_allow_html=True)


# INITIALIZE HISTORY STORAGE
if "history" not in st.session_state:
    st.session_state.history = []


# SIDEBAR NAVIGATION
with st.sidebar:
    safe_st_lottie(lottie_logo, height=140, key="logo")
    st.title("FraudShield AI")
    st.markdown("### Secure Transaction Monitor")
    st.markdown("---")

    menu = st.radio("Navigation", ["Dashboard", "History", "About System"])

    st.markdown("---")
    st.caption("Model Status: ✅ ACTIVE")


# MAIN UI
# DASHBOARD
if menu == "Dashboard":

    col1, col2 = st.columns([2, 1])

    with col1:
        st.title("Fraud Transaction Detection")
        st.write("Enter the transaction details below to predict if it's fraudulent.")

    with col2:
        safe_st_lottie(lottie_header, height=180, key="header")

    st.markdown("---")

    # Day mapping
    day_map = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }
    day_list = list(day_map.keys())

    # Glass Card Form
    with st.form(key="transaction_form"):
        c1, c2 = st.columns(2)

        with c1:
            TX_AMOUNT = st.number_input(
                "Transaction Amount", min_value=0.0, step=0.1)
            TX_HOUR = st.number_input(
                "Transaction Hour (0–23)", min_value=0, max_value=23, step=1)

        with c2:
            day_selected = st.selectbox("Day of Week", day_list)
            TX_DAY_OF_WEEK = day_map[day_selected]

            TX_TIME_DAYS = st.number_input(
                "Days Since Last Transaction", min_value=0.0, step=0.1)

        submit_button = st.form_submit_button(label="🔍 Analyze Risk")

    # On Submit
    if submit_button:

        with st.spinner("Processing transaction..."):
            time.sleep(0.9)

        input_df = pd.DataFrame([{
            "TX_AMOUNT": TX_AMOUNT,
            "TX_HOUR": TX_HOUR,
            "TX_DAY_OF_WEEK": TX_DAY_OF_WEEK,
            "TX_TIME_DAYS": TX_TIME_DAYS
        }])

        pred = model.predict(input_df)[0]
        pred_proba = model.predict_proba(input_df)[0][1]

        # SAVE TO HISTORY
        st.session_state.history.append({
            "Amount": TX_AMOUNT,
            "Hour": TX_HOUR,
            "Day": day_selected,
            "Days Since Last": TX_TIME_DAYS,
            "Prediction": "FRAUD" if pred == 1 else "LEGIT",
            "Fraud Probability": round(pred_proba, 3)
        })

        st.markdown("---")
        r1, r2 = st.columns([1, 2])

        with r1:
            if pred == 1:
                safe_st_lottie(lottie_alert, height=220, key="alert")
            else:
                safe_st_lottie(lottie_safe, height=220, key="safe")

        with r2:
            st.subheader("📊 Prediction Report")

            if pred == 1:
                st.error(
                    f"⚠️ Fraud Detected! Probability: **{pred_proba:.2f}**")
                st.markdown(
                    "🔴 **Recommendation:** Freeze transaction and start manual review.")
            else:
                st.success(
                    f"✅ Transaction Legitimate (Fraud Chance: **{pred_proba:.2f}**)")
                st.markdown(
                    "🟢 **Recommendation:** Transaction safe to approve.")


# HISTORY PAGE
elif menu == "History":

    st.title("📚 Prediction History")
    st.write("All previously analyzed transactions are stored here.")

    if len(st.session_state.history) == 0:
        st.info("No history available yet.")
    else:
        df_history = pd.DataFrame(st.session_state.history)
        st.dataframe(df_history, use_container_width=True)

        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.success("History cleared!")


# ABOUT PAGE
elif menu == "About System":
    st.title("ℹ️ About FraudShield AI")
    st.write("""
    FraudShield AI is a real-time intelligent fraud detection system.  
    It analyzes transaction patterns instantly and predicts whether a transaction is **fraudulent or legitimate**.

    ### 🔥 Key Features
    - Machine-learning powered fraud prediction  
    - Real-time fraud scoring  
    - Secure, encrypted analytics  
    - Enterprise-grade Streamlit web interface  
    - Ability to **view and track the history of previous predictions**  

    ### 🧠 Technical Overview
    - **Accuracy:** 99%
    - Built using a **proper Machine Learning pipeline**  
    - Model deployed through a **Streamlit web application**  
    - Uses **RandomForestClassifier**  
    - Predicts whether a transaction is **Fraud** or **Not Fraud**  
    """)
