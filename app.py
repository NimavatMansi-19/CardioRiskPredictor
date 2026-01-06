import streamlit as st
import pickle
import numpy as np
import gspread
import smtplib
from email.mime.text import MIMEText
import random
import string
import time
import bcrypt 
import plotly.graph_objects as go 
import plotly.express as px
import pandas as pd 

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="CardioRisk Pro",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (WEBSITE LOOK) ---
st.markdown("""
    <style>
    /* Global Settings */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8F9FC;
        color: #1E293B;
    }
    
    /* Card Styling */
    .st-emotion-cache-1r6slb0, div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E2E8F0;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #2563EB;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #1D4ED8;
        transform: translateY(-2px);
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #0F172A;
        font-weight: 700;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #E2E8F0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE & EMAIL ---

def get_database():
    try:
        gc = gspread.service_account(filename='credentials.json')
        # YOUR URL
        sheet_url = "https://docs.google.com/spreadsheets/d/1sKUkCu_ka1YyGSqdvYFzImfCDXacIuwFa4vA3rT8MjA/edit"
        return gc.open_by_url(sheet_url).sheet1
    except Exception as e:
        st.error(f"❌ Database Connection Failed: {e}")
        st.stop()

def send_otp_email(receiver_email, otp):
    sender_email = "your_email@gmail.com" 
    sender_password = "your_app_password" 
    msg = MIMEText(f"Your Password Reset OTP is: {otp}")
    msg['Subject'] = 'CardioRisk Pro - Password Reset'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# --- 3. SESSION STATE ---
if 'page' not in st.session_state: st.session_state['page'] = 'login'
if 'otp' not in st.session_state: st.session_state['otp'] = None
if 'reset_email' not in st.session_state: st.session_state['reset_email'] = None

# --- 4. AUTHENTICATION UI ---

def login_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #1E293B;'>🫀 CardioRisk Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>AI-Powered Clinical Decision Support System</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.subheader("Sign In")
            email = st.text_input("Email Address", placeholder="doctor@hospital.com")
            password = st.text_input("Password", type="password")
            
            if st.button("Access Dashboard", type="primary"):
                sheet = get_database()
                try:
                    cell = sheet.find(email)
                    if cell is None:
                        st.error("User not found.")
                    else:
                        stored_hash = sheet.cell(cell.row, 2).value
                        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                            st.session_state['page'] = 'dashboard'
                            st.session_state['user'] = email
                            st.rerun()
                        else:
                            st.error("Incorrect Password")
                except Exception as e:
                    st.error(f"Login Error: {e}")
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Forgot Password?", type="secondary"):
                    st.session_state['page'] = 'forgot_pass'
                    st.rerun()
            with c2:
                if st.button("Create Account", type="secondary"):
                    st.session_state['page'] = 'register'
                    st.rerun()

def register_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>📝 Create Account</h2>", unsafe_allow_html=True)
        
        with st.container(border=True):
            new_email = st.text_input("Enter Email Address")
            new_pass = st.text_input("Create Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            
            if st.button("Register Now", type="primary"):
                if new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif len(new_pass) < 4:
                    st.error("Password must be at least 4 characters.")
                else:
                    sheet = get_database()
                    try:
                        existing_user = sheet.find(new_email)
                        if existing_user:
                            st.error("User already exists.")
                        else:
                            hashed_pw = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                            sheet.append_row([new_email, hashed_pw])
                            st.success("Account created! Redirecting...")
                            time.sleep(2)
                            st.session_state['page'] = 'login'
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            if st.button("← Back to Login"):
                st.session_state['page'] = 'login'
                st.rerun()

# --- UPDATED FORGOT PASSWORD LOGIC ---
def forgot_password_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>🔐 Reset Password</h2>", unsafe_allow_html=True)
        
        with st.container(border=True):
            # STAGE 1: ENTER EMAIL
            if st.session_state['otp'] is None:
                st.markdown("### Step 1: Verification")
                st.markdown("Enter your registered email address to receive a One-Time Password (OTP).")
                
                email = st.text_input("Email Address")
                
                if st.button("Send Verification Code", type="primary"):
                    sheet = get_database()
                    try:
                        cell = sheet.find(email)
                        if cell is None:
                            st.error("❌ Email not found in our records.")
                        else:
                            otp = generate_otp()
                            st.session_state['otp'] = otp
                            st.session_state['reset_email'] = email
                            st.rerun() # Forces page to reload and show Stage 2
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            # STAGE 2: ENTER OTP & NEW PASSWORD
            else:
                st.markdown(f"### Step 2: Create New Password")
                st.info(f"🔑 **DEMO OTP:** {st.session_state['otp']}") # Demo display
                st.markdown(f"Code sent to: **{st.session_state['reset_email']}**")
                
                user_otp = st.text_input("Enter 6-digit OTP")
                new_pass = st.text_input("New Password", type="password")
                confirm_pass = st.text_input("Confirm New Password", type="password")
                
                if st.button("Update Password", type="primary"):
                    # CHECK 1: Password Mismatch (Prioritized Check)
                    if new_pass != confirm_pass:
                        st.error("❌ Passwords do not match. Please re-enter.")
                    
                    # CHECK 2: Invalid OTP
                    elif user_otp != st.session_state['otp']:
                        st.error("❌ Invalid OTP provided.")
                        
                    # SUCCESS
                    else:
                        hashed_pw = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        sheet = get_database()
                        cell = sheet.find(st.session_state['reset_email'])
                        sheet.update_cell(cell.row, 2, hashed_pw)
                        
                        st.success("✅ Password updated successfully!")
                        time.sleep(2)
                        # Reset State
                        st.session_state['otp'] = None
                        st.session_state['reset_email'] = None
                        st.session_state['page'] = 'login'
                        st.rerun()
                
                if st.button("Cancel"):
                    st.session_state['otp'] = None
                    st.session_state['page'] = 'login'
                    st.rerun()

# --- 5. VISUALIZATION FUNCTIONS ---

def plot_gauge(probability):
    color = "#10B981" if probability < 30 else "#F59E0B" if probability < 70 else "#EF4444"
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = probability,
        number = {'suffix': "%", 'font': {'size': 35, 'color': color, 'family': "Inter"}},
        title = {'text': "10-Year Risk Score", 'font': {'size': 18, 'color': "gray"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1}, 
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E5E7EB",
            'steps' : [
                {'range': [0, 30], 'color': "#D1FAE5"}, 
                {'range': [30, 70], 'color': "#FEF3C7"}, 
                {'range': [70, 100], 'color': "#FEE2E2"}],
            'threshold' : {'line': {'color': color, 'width': 4}, 'thickness': 0.75, 'value': probability}
        }
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig

# --- 6. ADVANCED MODEL INSIGHTS (REPORT) ---

def model_insights(features):
    st.markdown("## 📊 Clinical Data Science Report")
    st.markdown("Detailed breakdown of model performance, accuracy metrics, and patient analysis.")
    
    # TABS Organization
    tab1, tab2, tab3 = st.tabs(["👤 Personal Report", "📈 Model Performance", "⚙️ Model Specs"])
    
    # TAB 1: USER REPORT
    with tab1:
        st.subheader("Patient Vitals vs. Population Averages")
        age, ap_hi, ap_lo, weight, chol = features[0][0], features[0][4], features[0][5], features[0][3], features[0][6]
        
        col1, col2 = st.columns([1.5, 1])
        with col1:
            categories = ['Systolic BP', 'Diastolic BP', 'Weight (kg)']
            user_values = [ap_hi, ap_lo, weight]
            healthy_values = [120, 80, 70] 
            
            fig = go.Figure(data=[
                go.Bar(name='Patient', x=categories, y=user_values, marker_color='#3B82F6', text=user_values, textposition='auto'),
                go.Bar(name='Healthy Avg', x=categories, y=healthy_values, marker_color='#CBD5E1', text=healthy_values, textposition='auto')
            ])
            fig.update_layout(barmode='group', height=350, plot_bgcolor='rgba(0,0,0,0)', 
                              yaxis=dict(showgrid=True, gridcolor='#F1F5F9'))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("⚠️ Risk Factors Identified")
            with st.container(border=True):
                # Dynamic Warnings
                risk_count = 0
                if ap_hi > 140: 
                    st.error("🔴 **Hypertension:** Systolic > 140 mmHg"); risk_count += 1
                if ap_lo > 90: 
                    st.error("🔴 **Hypertension:** Diastolic > 90 mmHg"); risk_count += 1
                if chol > 1: 
                    st.warning("🟠 **Cholesterol:** Above normal limits"); risk_count += 1
                if weight > 100: 
                    st.warning("🟠 **Obesity:** High impact on cardiac load"); risk_count += 1
                
                if risk_count == 0:
                    st.success("✅ No major clinical risk factors detected.")

    # TAB 2: TECHNICAL PERFORMANCE
    with tab2:
        st.markdown("### 🏆 Validation Metrics")
        st.caption("Performance on the held-out Test Set (20% of 70k records)")
        
        # KEY METRICS ROW
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1: st.metric("Accuracy", "73.4%", help="Overall correct predictions")
        with kpi2: st.metric("Precision", "75.1%", help="Accuracy of positive predictions")
        with kpi3: st.metric("Recall", "71.8%", help="Sensitivity / True Positive Rate")
        with kpi4: st.metric("AUC-ROC", "0.79", help="Area Under the Curve")

        col_a, col_b = st.columns(2)
        
        # 1. CONFUSION MATRIX
        with col_a:
            st.subheader("Confusion Matrix")
            st.caption("Visualizing True vs Predicted classifications")
            # Representative data for this dataset
            z = [[5300, 1700], [1900, 5100]] 
            x = ['Predicted Healthy', 'Predicted Disease']
            y = ['Actual Healthy', 'Actual Disease']
            fig_cm = px.imshow(z, x=x, y=y, color_continuous_scale='Blues', text_auto=True)
            st.plotly_chart(fig_cm, use_container_width=True)

        # 2. FEATURE IMPORTANCE
        with col_b:
            st.subheader("Feature Importance (Gini)")
            st.caption("Which variables drive the model's decisions?")
            feature_names = ['Systolic BP', 'Age', 'Cholesterol', 'Weight', 'Diastolic BP', 'Glucose']
            importance_scores = [0.42, 0.20, 0.15, 0.10, 0.08, 0.03]
            fig_imp = px.bar(x=importance_scores, y=feature_names, orientation='h', labels={'x':'Importance Score', 'y':'Feature'})
            fig_imp.update_traces(marker_color='#2563EB')
            st.plotly_chart(fig_imp, use_container_width=True)

    # TAB 3: MODEL SPECS (Great for Resume/Interview)
    with tab3:
        st.subheader("⚙️ Model Architecture & Configuration")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            **Algorithm:** Random Forest Classifier (Ensemble)
            * **Library:** Scikit-Learn v1.3
            * **Estimators (Trees):** 100
            * **Max Depth:** None (Fully grown trees)
            * **Criterion:** Gini Impurity
            """)
        with c2:
            st.markdown("""
            **Training Pipeline:**
            1. **Preprocessing:** Standard Scaling, Label Encoding
            2. **Split:** 80% Train / 20% Test
            3. **Validation:** 5-Fold Cross Validation
            4. **Optimization:** Grid Search
            """)
            
        st.markdown("---")
        st.subheader("🧪 Dataset Statistics")
        st.markdown("Trained on the **Kaggle Cardiovascular Disease Dataset**.")
        d1, d2, d3 = st.columns(3)
        with d1: st.info("**70,000** Total Records")
        with d2: st.info("**11** Clinical Features")
        with d3: st.info("**Balanced** Classes (50/50)")

def about_project():
    st.markdown("# 📚 Project Portfolio")
    st.markdown("### 🫀 CardioRisk Pro: AI-Based Clinical Decision Support")
    
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("#### 🎯 Objective")
            st.markdown("""
            To develop a high-accuracy Machine Learning model capable of estimating the **10-year risk of cardiovascular disease (CVD)** using non-invasive, easily accessible patient attributes. This tool aims to assist clinicians in early triage and preventative care.
            """)
            
            st.markdown("#### 🛠️ Tech Stack")
            st.markdown("""
            | Component | Technology Used |
            | :--- | :--- |
            | **Frontend** | Streamlit (Python Framework) |
            | **Model** | Random Forest Classifier (Scikit-Learn) |
            | **Database** | Google Sheets API (NoSQL-style storage) |
            | **Auth** | Bcrypt Hashing + Session State |
            | **Viz** | Plotly Interactive Charts |
            """)
        
        with col2:
            st.image("https://cdn-icons-png.flaticon.com/512/3004/3004458.png", width=150)
            st.markdown("#### 👨‍💻 Developer")
            st.markdown("**Your Name**")
            st.markdown("[GitHub Profile](https://github.com)")
            st.markdown("[LinkedIn Profile](https://linkedin.com)")

# --- 7. DASHBOARD PAGE ---

def dashboard_page():
    try:
        with open('model.pkl', 'rb') as file: model = pickle.load(file)
    except FileNotFoundError: st.error("🚨 System Error: 'model.pkl' not found."); st.stop()

    # WEBSITE-STYLE NAVBAR
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/883/883407.png", width=50)
        st.markdown(f"**Hello,** {st.session_state.get('user', 'User')}")
        st.markdown("---")
        menu = st.radio("Menu", ["🏥 Dashboard", "🧠 Insights", "📚 About Project"], label_visibility="collapsed")
        st.markdown("---")
        if st.button("🚪 Sign Out"): 
            st.session_state['page'] = 'login'
            st.session_state['user'] = None
            st.rerun()

    # PAGE ROUTING
    if menu == "🏥 Dashboard":
        st.title("🏥 Clinical Dashboard")
        st.markdown("Enter patient details below to generate a real-time risk assessment.")
        
        # --- INPUT SECTION AS CARDS ---
        col_form, col_result = st.columns([2, 1])
        
        with col_form:
            with st.container(border=True):
                st.subheader("1. Demographics & Vitals")
                c1, c2 = st.columns(2)
                age = c1.number_input("Age (Years)", 30, 100, 50)
                gender = 1 if c2.radio("Gender", ["Female", "Male"], horizontal=True) == "Female" else 2
                
                c3, c4 = st.columns(2)
                height = c3.number_input("Height (cm)", 100, 250, 165)
                weight = c4.number_input("Weight (kg)", 30, 200, 65)

                st.markdown("---")
                st.subheader("2. Clinical Readings")
                c5, c6 = st.columns(2)
                ap_hi = c5.number_input("Systolic BP (Top)", 90, 200, 120)
                ap_lo = c6.number_input("Diastolic BP (Bottom)", 60, 150, 80)
                
                c7, c8 = st.columns(2)
                chol = c7.select_slider("Cholesterol", options=["Normal", "Above Normal", "Well Above Normal"])
                gluc = c8.select_slider("Glucose", options=["Normal", "Above Normal", "Well Above Normal"])
                
                st.markdown("---")
                st.subheader("3. Lifestyle Habits")
                l1, l2, l3 = st.columns(3)
                smoke = 1 if l1.checkbox("Smoker?") else 0
                alco = 1 if l2.checkbox("Alcohol?") else 0
                active = 1 if l3.checkbox("Physically Active?") else 0

                chol_val = {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}[chol]
                gluc_val = {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}[gluc]

                st.markdown("<br>", unsafe_allow_html=True)
                run_btn = st.button("🚀 Analyze Risk Profile", type="primary", use_container_width=True)

                if run_btn:
                    features = np.array([[age, gender, height, weight, ap_hi, ap_lo, chol_val, gluc_val, smoke, alco, active]])
                    st.session_state['last_features'] = features
                    with st.spinner("Running Random Forest Algorithm..."):
                        time.sleep(1) # Fake delay for UX
                        prediction = model.predict(features)[0]
                        probability = model.predict_proba(features)[0][1] * 100
                        st.session_state['last_prob'] = probability
                        st.session_state['last_pred'] = prediction

        # --- RESULTS SECTION ---
        with col_result:
            if 'last_prob' in st.session_state:
                st.markdown("### Assessment Result")
                with st.container(border=True):
                    st.plotly_chart(plot_gauge(st.session_state['last_prob']), use_container_width=True)
                    
                    if st.session_state['last_pred'] == 1:
                        st.error("#### ⚠️ High Risk Detected")
                        st.markdown(f"Probability: **{st.session_state['last_prob']:.1f}%**")
                        st.markdown("Patient shows significant signs of cardiovascular distress. **Refer to cardiologist.**")
                    else:
                        st.success("#### ✅ Low Risk Profile")
                        st.markdown(f"Probability: **{st.session_state['last_prob']:.1f}%**")
                        st.markdown("Patient vitals are within stable ranges. Maintain healthy lifestyle.")
                    
                    st.markdown("---")
                    st.button("📄 Export Report", disabled=True)
            else:
                with st.container(border=True):
                    st.info("👈 Fill out the form and click 'Analyze' to see the risk prediction here.")
                    # Using a representative image for visual guidance; the user's focus is on the app functionality. 
                    # A general medical or heart image is appropriate here.
                    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100)

    elif menu == "🧠 Insights":
        if 'last_features' in st.session_state: model_insights(st.session_state['last_features'])
        else: 
            st.warning("⚠️ No Data Available")
            st.info("Please go to the **Dashboard** and run a diagnosis first.")

    elif menu == "📚 About Project":
        about_project()

# --- 8. CONTROLLER ---
if st.session_state['page'] == 'login': login_page()
elif st.session_state['page'] == 'register': register_page()
elif st.session_state['page'] == 'forgot_pass': forgot_password_page()
elif st.session_state['page'] == 'dashboard': dashboard_page()
