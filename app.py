import streamlit as st
import joblib
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Morning Star Hospital", page_icon="🏥", layout="centered")

st.markdown("""
<style>
.main{background:linear-gradient(135deg,#f5f0ff 0%,#ffffff 100%)}
.card{background:white;border-radius:16px;padding:2rem;box-shadow:0 4px 24px rgba(107,33,168,0.1);margin-bottom:1.5rem}
.dbh{background:linear-gradient(135deg,#4B0082,#9333EA);color:white;padding:1.5rem 2rem;border-radius:16px;margin-bottom:1.5rem}
.dbh h2{font-size:1.4rem;font-weight:600;margin:0;color:white}
.dbh p{font-size:0.85rem;opacity:0.8;margin:4px 0 0 0}
.risk-low{background:#ECFDF5;border-left:5px solid #059669;padding:1.2rem;border-radius:12px;color:#065F46;font-size:1.1rem;font-weight:600}
.risk-moderate{background:#FFFBEB;border-left:5px solid #D97706;padding:1.2rem;border-radius:12px;color:#92400E;font-size:1.1rem;font-weight:600}
.risk-high{background:#FEF2F2;border-left:5px solid #DC2626;padding:1.2rem;border-radius:12px;color:#7F1D1D;font-size:1.1rem;font-weight:600}
.sec{font-size:1rem;font-weight:600;color:#4B0082;margin-bottom:0.5rem;padding-bottom:0.3rem;border-bottom:2px solid #EDE9FE}
.stButton>button{background:linear-gradient(135deg,#6B21A8,#9333EA)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:600!important;width:100%!important}
.foot{text-align:center;font-size:0.75rem;color:#aaa;margin-top:2rem;padding-top:1rem;border-top:1px solid #EDE9FE}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

USERS = {"doctor":"adun2026","nurse":"nurse2026","admin":"admin2026"}
MODEL_PATH  = "/Users/mac/Desktop/PROJECT/diabetes_model.pkl"
SCALER_PATH = "/Users/mac/Desktop/PROJECT/diabetes_scaler.pkl"
CSV_PATH    = "/Users/mac/Desktop/PROJECT/patient_records.csv"

if not st.session_state.logged_in:
    st.markdown("<div style=text-align:center;padding:2rem 0 1rem><div style=font-size:3rem>🏥</div><h1 style=color:#4B0082>Morning Star Hospital</h1><p style=color:#888>Diabetes Risk Prediction System</p><span style=background:linear-gradient(135deg,#6B21A8,#9333EA);color:white;padding:6px 16px;border-radius:20px;font-size:0.75rem>No. 19/21 Isiokpo Street, D-Line, Port Harcourt</span></div>", unsafe_allow_html=True)
    st.markdown("<div class=card>", unsafe_allow_html=True)
    st.markdown("<p class=sec>🔐 Staff Login</p>", unsafe_allow_html=True)
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class=foot>A Comparative Wrapper Based Approach for Predicting Diabetes | Murray-Bruce Ayebatari Stephanie | ADUN/FS/CSC/22/017 | ADUN 2026</div>", unsafe_allow_html=True)

else:
    model  = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    st.markdown(f"<div class=dbh><h2>🏥 Diabetes Risk Prediction System</h2><p>Morning Star Hospital, Port Harcourt | Logged in as: <strong>{st.session_state.username}</strong></p></div>", unsafe_allow_html=True)
    st.markdown("<div class=card>", unsafe_allow_html=True)
    st.markdown("<p class=sec>👤 Patient Details</p>", unsafe_allow_html=True)
    patient_id = st.text_input("Patient ID", placeholder="e.g. MSH-001")
    col1, col2 = st.columns(2)
    with col1:
        glucose = st.number_input("Glucose Level (mg/dL)", min_value=50.0, max_value=200.0, value=100.0)
        age     = st.number_input("Age (years)", min_value=18, max_value=90, value=30)
    with col2:
        bmi = st.number_input("BMI (kg/m2)", min_value=10.0, max_value=100.0, value=25.0)
        bp  = st.number_input("Blood Pressure (mmHg)", min_value=40.0, max_value=130.0, value=70.0)
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Predict Diabetes Risk"):
        if not patient_id:
            st.warning("Please enter a Patient ID.")
        else:
            input_data   = pd.DataFrame([[bmi, age, glucose, bp]], columns=scaler.feature_names_in_)
            input_scaled = scaler.transform(input_data)
            prob         = model.predict_proba(input_scaled)[0][1] * 100
            if prob < 30:
                risk = "LOW"
                st.markdown(f"<div class=risk-low>✅ LOW RISK — {prob:.1f}%</div>", unsafe_allow_html=True)
                st.info("Routine screening in 3 years. Maintain a healthy diet and regular exercise.")
            elif prob < 60:
                risk = "MODERATE"
                st.markdown(f"<div class=risk-moderate>⚠️ MODERATE RISK — {prob:.1f}%</div>", unsafe_allow_html=True)
                st.info("Lifestyle changes recommended. Re-screen in 12 months.")
            else:
                risk = "HIGH"
                st.markdown(f"<div class=risk-high>🚨 HIGH RISK — {prob:.1f}%</div>", unsafe_allow_html=True)
                st.info("Refer to endocrinologist. Confirm with HbA1c test immediately.")
            record = {"Patient ID":patient_id,"Glucose":glucose,"BMI":bmi,"Age":age,"Blood Pressure":bp,"Risk Score (%)":round(prob,1),"Risk Level":risk,"Date":datetime.now().strftime("%d/%m/%Y %H:%M"),"Assessed By":st.session_state.username}
            if os.path.exists(CSV_PATH):
                df_new = pd.concat([pd.read_csv(CSV_PATH), pd.DataFrame([record])], ignore_index=True)
            else:
                df_new = pd.DataFrame([record])
            df_new.to_csv(CSV_PATH, index=False)
            st.success(f"✅ Record saved for Patient {patient_id}!")
    st.markdown("<div class=card>", unsafe_allow_html=True)
    st.markdown("<p class=sec>📋 Patient Records</p>", unsafe_allow_html=True)
    if os.path.exists(CSV_PATH):
        df_records = pd.read_csv(CSV_PATH)
        st.dataframe(df_records, use_container_width=True)
        st.download_button("📥 Download Records as CSV", df_records.to_csv(index=False), "patient_records.csv", "text/csv", use_container_width=True)
    else:
        st.info("No records saved yet.")
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
    st.markdown("<div class=foot>Research prototype — not a substitute for professional medical diagnosis.<br>Murray-Bruce Ayebatari Stephanie | ADUN/FS/CSC/22/017 | ADUN 2026</div>", unsafe_allow_html=True)
