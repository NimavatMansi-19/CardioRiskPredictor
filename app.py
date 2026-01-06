import streamlit as st
import pickle
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
import random
import string
import time
import bcrypt  # For secure password hashing

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="CardioRisk Pro",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GOOGLE SHEETS & EMAIL SETUP ---

# Function to connect to Google Sheets
def get_database():
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Authenticate (Ensure credentials.json is in your folder)
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        # Open the sheet - MAKE SURE you create a sheet named 'CardioUsers'
        sheet = client.open("CardioUsers").sheet1
        return sheet
    except Exception as e:
        st.error(f"❌ Database Connection Error: {e}")
        st.stop()

# Function to send OTP via Email
def send_otp_email(receiver_email, otp):
    # --- CONFIGURE THIS ---
    sender_email = "your_email@gmail.com" 
    sender_password = "your_app_password" # Use App Password, not login password
    # ----------------------
    
    msg = MIMEText(f"Your Password Reset OTP is: {otp}")
    msg['Subject'] = 'CardioRisk Pro - Password Reset'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

# Helper: Generate Random OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# --- 3. SESSION STATE MANAGEMENT ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'login' # Options: login, forgot_pass, dashboard
if 'otp' not in st.session_state:
    st.session_state['otp'] = None
if 'reset_email' not in st.session_state:
    st.session_state['reset_email'] = None

# --- 4. AUTHENTICATION UI PAGES ---

def login_page():
    st.markdown("<h1 style='text-align: center;'>🫀 CardioRisk Pro Login</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("Login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                sheet = get_database()
                try:
                    # Find user by email (Assuming Email is in Column A, Password in Column B)
                    cell = sheet.find(email)
                    stored_hash = sheet.cell(cell.row, 2).value # Get password from Col B
                    
                    # Verify Password
                    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                        st.session_state['page'] = 'dashboard'
                        st.session_state['user'] = email
                        st.rerun()
                    else:
                        st.error("Incorrect Password")
                except gspread.exceptions.CellNotFound:
                    st.error("User not found.")
                except Exception as e:
                    st.error(f"Login Error: {e}")

        if st.button("Forgot Password?"):
            st.session_state['page'] = 'forgot_pass'
            st.rerun()

def forgot_password_page():
    st.markdown("## 🔐 Reset Password")
    
    # Step 1: Request OTP
    if st.session_state['otp'] is None:
        email = st.text_input("Enter your registered email")
        if st.button("Send OTP"):
            sheet = get_database()
            try:
                # Check if email exists
                cell = sheet.find(email)
                
                # Generate and Send OTP
                otp = generate_otp()
                st.session_state['otp'] = otp
                st.session_state['reset_email'] = email
                
                # --- EMAIL SENDING ---
                # Uncomment the line below to actually send email
                # send_success = send_otp_email(email, otp) 
                
                # FOR DEMO ONLY: Print OTP to screen so you can test without SMTP setup
                st.info(f"DEMO MODE: Your OTP is {otp}") 
                send_success = True 
                
                if send_success:
                    st.success("OTP sent to your email!")
            except gspread.exceptions.CellNotFound:
                st.error("Email not found in our database.")
    
    # Step 2: Verify OTP and Change Password
    else:
        st.info(f"OTP sent to {st.session_state['reset_email']}")
        
        with st.form("Reset"):
            user_otp = st.text_input("Enter 6-digit OTP")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            submit_reset = st.form_submit_button("Update Password")
            
            if submit_reset:
                if user_otp == st.session_state['otp']:
                    if new_pass == confirm_pass:
                        # Hash new password
                        hashed_pw = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        
                        # Update Google Sheet
                        sheet = get_database()
                        cell = sheet.find(st.session_state['reset_email'])
                        sheet.update_cell(cell.row, 2, hashed_pw) # Updating Col 2 (Password)
                        
                        st.success("Password Updated Successfully! Redirecting to login...")
                        time.sleep(2)
                        
                        # Reset State
                        st.session_state['otp'] = None
                        st.session_state['reset_email'] = None
                        st.session_state['page'] = 'login'
                        st.rerun()
                    else:
                        st.error("Passwords do not match.")
                else:
                    st.error("Invalid OTP.")

        if st.button("Cancel"):
            st.session_state['otp'] = None
            st.session_state['page'] = 'login'
            st.rerun()

# --- 5. MAIN DASHBOARD (Your Original App) ---

def dashboard_page():
    # Logout Button
    with st.sidebar:
        if st.button("🚪 Logout"):
            st.session_state['page'] = 'login'
            st.rerun()

    # Custom CSS
    st.markdown("""
        <style>
        .main { background-color: #f5f5f5; }
        .stButton>button { width: 100%; background-color: #ff4b4b; color: white; height: 3em; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

    # Load Model
    try:
        with open('model.pkl', 'rb') as file:
            model = pickle.load(file)
    except FileNotFoundError:
        st.error("🚨 System Error: 'model.pkl' not found.")
        st.stop()

    # Sidebar
    st.sidebar.header("📋 Patient Data Entry")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Demographics")
    age = st.sidebar.number_input("Age (Years)", 30, 100, 50)
    gender_txt = st.sidebar.radio("Gender", ["Female", "Male"], horizontal=True)
    height = st.sidebar.number_input("Height (cm)", 100, 250, 165)
    weight = st.sidebar.number_input("Weight (kg)", 30, 200, 65)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Medical Vitals")
    ap_hi = st.sidebar.number_input("Systolic BP (Top #)", 90, 200, 120)
    ap_lo = st.sidebar.number_input("Diastolic BP (Bottom #)", 60, 150, 80)
    chol_txt = st.sidebar.selectbox("Cholesterol", ["Normal", "Above Normal", "Well Above Normal"])
    gluc_txt = st.sidebar.selectbox("Glucose", ["Normal", "Above Normal", "Well Above Normal"])
    st.sidebar.markdown("---")
    st.sidebar.subheader("Lifestyle Habits")
    smoke_txt = st.sidebar.selectbox("Smoker?", ["No", "Yes"])
    alco_txt = st.sidebar.selectbox("Alcohol Intake?", ["No", "Yes"])
    active_txt = st.sidebar.selectbox("Physically Active?", ["No", "Yes"])

    # Main Page
    st.title("🫀 CardioRisk Pro")
    st.markdown("### AI-Powered Cardiovascular Disease Assessment")

    with st.expander("👀 Review Patient Summary", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Age", f"{age} yrs")
        c2.metric("BMI", f"{weight/((height/100)**2):.1f}")
        c3.metric("BP", f"{ap_hi}/{ap_lo}")
        c4.metric("Active?", active_txt)

    # Logic
    gender = 1 if gender_txt == "Female" else 2
    chol_map = {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}
    cholesterol = chol_map[chol_txt]
    gluc_map = {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}
    gluc = gluc_map[gluc_txt]
    smoke = 1 if smoke_txt == "Yes" else 0
    alco = 1 if alco_txt == "Yes" else 0
    active = 1 if active_txt == "Yes" else 0

    if st.sidebar.button("RUN DIAGNOSIS"):
        with st.spinner("Analyzing clinical data..."):
            features = np.array([[age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active]])
            prediction = model.predict(features)[0]
            probability = model.predict_proba(features)[0][1]
            prob_percent = probability * 100

        st.divider()
        col_res1, col_res2 = st.columns([2, 1])
        with col_res1:
            if prediction == 1:
                st.error("## ⚠️ High Risk Detected")
                st.write("The model predicts a high likelihood of cardiovascular disease.")
                st.write("**Recommendation:** Immediate clinical consultation advised.")
            else:
                st.success("## ✅ Low Risk / Healthy")
                st.write("The model predicts a low likelihood of cardiovascular disease.")
        with col_res2:
            st.metric(label="Risk Probability", value=f"{prob_percent:.1f}%")
            st.progress(int(prob_percent))
        st.warning("⚠️ Disclaimer: Educational purposes only.")

# --- 6. APP CONTROLLER ---
# This controls which page is currently shown

if st.session_state['page'] == 'login':
    login_page()
elif st.session_state['page'] == 'forgot_pass':
    forgot_password_page()
elif st.session_state['page'] == 'dashboard':
    dashboard_page()
