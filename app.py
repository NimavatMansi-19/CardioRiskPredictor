import streamlit as st
import pickle
import numpy as np
import pandas as pd
import time
import sqlite3
import hashlib

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="MediPredict | Clinical Dashboard",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: #2c3e50; }
    .css-1r6slb0, .css-12oz5g7 { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button { background-color: #007bff; color: white; border-radius: 8px; height: 50px; font-size: 18px; border: none; }
    .stButton>button:hover { background-color: #0056b3; }
    /* Success Message Style */
    .stSuccess { background-color: #d4edda; color: #155724; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE MANAGEMENT FUNCTIONS ---

def make_hashes(password):
    """Encrypt password before saving to DB"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    """Check if entered password matches the saved hash"""
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def create_usertable():
    """Create the table if it doesn't exist"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        # This line will fail if username already exists
        c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False # <--- This handles the "User Already Exists" error
    conn.close()
    return success

def login_user(username, password):
    """Verify login credentials"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    conn.close()
    return data

# Initialize DB on first run
create_usertable()

# --- 4. AUTHENTICATION LOGIC (LOGIN / SIGNUP) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

def auth_screen():
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("Welcome to MediPredict")
    st.markdown("Please Login or Register to access the Clinical Dashboard.")

    # Create Tabs for Login and Sign Up
    tab1, tab2 = st.tabs(["🔒 Login", "📝 Sign Up (Register)"])

    # --- LOGIN TAB ---
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.subheader("Login Section")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Login"):
                hashed_pswd = make_hashes(password)
                result = login_user(username, hashed_pswd)
                
                if result:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.success(f"Welcome back, {username}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Incorrect Username or Password")

    # --- SIGN UP TAB ---
   # --- SIGN UP TAB ---
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.subheader("Create New Account")
            new_user = st.text_input("New Username", key="new_user")
            new_password = st.text_input("New Password", type="password", key="new_pass")
            
            if st.button("Register"):
                if new_user and new_password:
                    hashed_new_password = make_hashes(new_password)
                    
                    # Try to add the user
                    is_created = add_userdata(new_user, hashed_new_password)
                    
                    if is_created:
                        st.success("✅ Account created successfully!")
                        st.info("Please navigate to the Login tab to sign in.")
                    else:
                        # This message appears if the user is already in the DB
                        st.error("⚠️ Error: User already exists!")
                        st.warning(f"The username '{new_user}' is already registered. Please choose a different ID or Login.")
                else:
                    st.error("Please enter both a username and password.")
# --- 5. MAIN APPLICATION ---

if not st.session_state['logged_in']:
    auth_screen()
else:
    # --- Load Model ---
    try:
        with open('model.pkl', 'rb') as file:
            model = pickle.load(file)
    except FileNotFoundError:
        st.error("System Error: Model file missing.")
        st.stop()

    # --- SIDEBAR NAVIGATION ---
    st.sidebar.title(f"👤 Dr. {st.session_state['username']}")
    st.sidebar.caption("Authorized Personnel")
    st.sidebar.divider()
    
    page = st.sidebar.radio("Navigation", ["Clinical Dashboard", "Model Insights"], index=0)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # =========================================
    # PAGE 1: CLINICAL DASHBOARD
    # =========================================
    if page == "Clinical Dashboard":
        st.title("⚕️ Patient Assessment")
        
        left_column, right_column = st.columns([2, 1])

        with left_column:
            st.subheader("Patient Intake Form")
            tab_p, tab_v, tab_h = st.tabs(["Profile", "Vitals", "History"])
            
            with tab_p:
                c1, c2 = st.columns(2)
                age = c1.number_input("Age", 18, 100, 50)
                gender_txt = c2.selectbox("Gender", ["Female", "Male"])
                c3, c4 = st.columns(2)
                height = c3.number_input("Height (cm)", 100, 250, 165)
                weight = c4.number_input("Weight (kg)", 30, 200, 70)
                st.info(f"BMI: {weight / ((height/100)**2):.2f}")

            with tab_v:
                c1, c2 = st.columns(2)
                ap_hi = c1.number_input("Systolic BP", 80, 220, 120)
                ap_lo = c2.number_input("Diastolic BP", 50, 150, 80)
                c3, c4 = st.columns(2)
                chol_txt = c3.selectbox("Cholesterol", ["Normal", "Above Normal", "Well Above Normal"])
                gluc_txt = c4.selectbox("Glucose", ["Normal", "Above Normal", "Well Above Normal"])

            with tab_h:
                c1, c2, c3 = st.columns(3)
                smoke_txt = c1.radio("Smoker?", ["No", "Yes"])
                alco_txt = c2.radio("Alcohol?", ["No", "Yes"])
                active_txt = c3.radio("Active?", ["No", "Yes"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            run_prediction = st.button("Run Analysis", type="primary")

        with right_column:
            st.subheader("Results")
            res_container = st.container()
            with res_container:
                st.info("Awaiting Input...")

            if run_prediction:
                with st.spinner("Analyzing..."):
                    time.sleep(0.5)
                
                # Conversion
                gender = 1 if gender_txt == "Female" else 2
                cholesterol = {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}[chol_txt]
                gluc = {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}[gluc_txt]
                smoke = 1 if smoke_txt == "Yes" else 0
                alco = 1 if alco_txt == "Yes" else 0
                active = 1 if active_txt == "Yes" else 0

                features = np.array([[age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active]])
                prediction = model.predict(features)[0]
                probability = model.predict_proba(features)[0][1] * 100

                res_container.empty()
                with res_container:
                    if prediction == 1:
                        st.error("HIGH RISK DETECTED")
                        st.metric("Risk", f"{probability:.1f}%", "High Alert", delta_color="inverse")
                        st.progress(int(probability))
                    else:
                        st.success("LOW RISK / HEALTHY")
                        st.metric("Risk", f"{probability:.1f}%", "- Safe")
                        st.progress(int(probability))

    # =========================================
    # PAGE 2: MODEL INSIGHTS
    # =========================================
    elif page == "Model Insights":
        st.title("🧠 Model Transparency Report")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Algorithm", "Decision Tree")
        col2.metric("Training Data", "70,000 Pts")
        col3.metric("Depth", "10 Levels")
        st.divider()

        st.subheader("Feature Importance")
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_names = ['Age', 'Gender', 'Height', 'Weight', 'Systolic BP', 'Diastolic BP', 'Cholesterol', 'Glucose', 'Smoking', 'Alcohol', 'Activity']
            df_imp = pd.DataFrame({'Feature': feature_names, 'Importance': importance})
            df_imp = df_imp.sort_values(by='Importance', ascending=True)
            st.bar_chart(df_imp.set_index('Feature'))
        else:
            st.warning("Feature importance not available.")
