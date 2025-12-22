import streamlit as st
import pickle
import numpy as np

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="CardioRisk Pro",
    page_icon="🫀",
    layout="wide",  # Uses the full width of the screen
    initial_sidebar_state="expanded"
)

# Custom CSS to make it look cleaner
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Load Model
try:
    with open('model.pkl', 'rb') as file:
        model = pickle.load(file)
except FileNotFoundError:
    st.error("🚨 System Error: 'model.pkl' not found. Please verify the file exists.")
    st.stop()


# --- 2. SIDEBAR (INPUT DATA) ---
st.sidebar.header("📋 Patient Data Entry")
st.sidebar.markdown("---")

# Section A: Demographics
st.sidebar.subheader("Demographics")
age = st.sidebar.number_input("Age (Years)", 30, 100, 50)
gender_txt = st.sidebar.radio("Gender", ["Female", "Male"], horizontal=True)
height = st.sidebar.number_input("Height (cm)", 100, 250, 165)
weight = st.sidebar.number_input("Weight (kg)", 30, 200, 65)

st.sidebar.markdown("---")

# Section B: Vitals
st.sidebar.subheader("Medical Vitals")
ap_hi = st.sidebar.number_input("Systolic BP (Top #)", 90, 200, 120)
ap_lo = st.sidebar.number_input("Diastolic BP (Bottom #)", 60, 150, 80)
chol_txt = st.sidebar.selectbox("Cholesterol", ["Normal", "Above Normal", "Well Above Normal"])
gluc_txt = st.sidebar.selectbox("Glucose", ["Normal", "Above Normal", "Well Above Normal"])

st.sidebar.markdown("---")

# Section C: Lifestyle
st.sidebar.subheader("Lifestyle Habits")
smoke_txt = st.sidebar.selectbox("Smoker?", ["No", "Yes"])
alco_txt = st.sidebar.selectbox("Alcohol Intake?", ["No", "Yes"])
active_txt = st.sidebar.selectbox("Physically Active?", ["No", "Yes"])


# --- 3. MAIN PAGE (DASHBOARD) ---
st.title("🫀 CardioRisk Pro")
st.markdown("### AI-Powered Cardiovascular Disease Assessment")
st.markdown("Use the sidebar to enter patient details. The Artificial Intelligence model will evaluate the risk profile based on clinical parameters.")

# Display a summary of input (Optional visual check for doctor)
with st.expander("👀 Review Patient Summary", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Age", f"{age} yrs")
    c2.metric("BMI (Approx)", f"{weight/((height/100)**2):.1f}")
    c3.metric("BP", f"{ap_hi}/{ap_lo}")
    c4.metric("Active?", active_txt)


# --- 4. PREDICTION LOGIC ---

# Conversion Logic
gender = 1 if gender_txt == "Female" else 2
chol_map = {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}
cholesterol = chol_map[chol_txt]
gluc_map = {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}
gluc = gluc_map[gluc_txt]
smoke = 1 if smoke_txt == "Yes" else 0
alco = 1 if alco_txt == "Yes" else 0
active = 1 if active_txt == "Yes" else 0

# The Button
if st.sidebar.button("RUN DIAGNOSIS"):
    
    # Spinner while processing
    with st.spinner("Analyzing clinical data..."):
        
        # Prepare Data
        features = np.array([[age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active]])
        
        # Predict
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1] # Probability of "1" (Disease)
        prob_percent = probability * 100

    # Layout for Results
    st.divider()
    
    col_res1, col_res2 = st.columns([2, 1])

    with col_res1:
        if prediction == 1:
            st.error("## ⚠️ High Risk Detected")
            st.write("The model predicts a high likelihood of cardiovascular disease presence based on the provided vitals.")
            st.write("**Recommendation:** Immediate clinical consultation is advised.")
        else:
            st.success("## ✅ Low Risk / Healthy")
            st.write("The model predicts a low likelihood of cardiovascular disease.")
            st.write("**Recommendation:** Maintain a healthy lifestyle and regular checkups.")

    with col_res2:
        st.metric(label="Risk Probability", value=f"{prob_percent:.1f}%")
        st.write("Risk Gauge:")
        
        # Color of bar changes based on risk
        bar_color = "red" if prob_percent > 50 else "green"
        st.progress(int(prob_percent))
        
    # Disclaimer
    st.warning("⚠️ Disclaimer: This tool is for educational purposes only and is not a substitute for professional medical diagnosis.")

else:
    # Placeholder when no prediction is made yet
    st.info("👈 Please enter patient data in the sidebar and click 'RUN DIAGNOSIS' to start.")