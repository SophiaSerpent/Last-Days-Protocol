#         SOPHIA SERPENT 
#  The Architects of The New World 
#   The Future Was Built on Web3


import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier

# --- SYSTEM INITIALIZATION ---
yf.set_tz_cache_location("/tmp")
st.set_page_config(page_title="SOPHIA SERPENT COMMAND", layout="wide", initial_sidebar_state="collapsed")

# --- UI THEME: DEEP BLACK ---
st.markdown("""
    <style>
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #000000 !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #FFFFFF !important; font-family: 'Courier New', Courier, monospace; }
    [data-testid="stMetricValue"] { color: #00FF41 !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    div.stButton > button:first-child {
        background-color: #000000; color: #00FF41; border: 2px solid #00FF41;
        border-radius: 0px; width: 100%; font-weight: bold;
    }
    div.stButton > button:hover { background-color: #00FF41; color: #000000; }
    .stAlert { background-color: #000000 !important; border: 1px solid #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LIVE MARKET DATA ASSETS (FEB 20, 2026) ---
KINETIC_ASSETS = {
    "Lockheed Martin (LMT)": 666.51,
    "RTX Corp (RTX)": 204.92,
    "Northrop Grumman (NOC)": 736.87,
    "General Dynamics (GD)": 344.86,
    "Boeing (BA)": 242.32
}

CYBER_ASSETS = {
    "CrowdStrike (CRWD)": 405.07,
    "Palo Alto (PANW)": 392.12,
    "Palantir (PLTR)": 48.75,
    "Fortinet (FTNT)": 84.30,
    "CACI International (CACI)": 465.15
}

# --- BACKEND LOGIC ---
def run_audit_logic():
    steel = ["LMT", "RTX", "NOC", "GD", "BA"]
    cyber = ["CRWD", "PANW", "PLTR", "FTNT", "CACI"]
    
    s_data = yf.download(steel, period="2y", interval="1d", progress=False)['Close'].mean(axis=1)
    c_data = yf.download(cyber, period="2y", interval="1d", progress=False)['Close'].mean(axis=1)
    
    df = pd.DataFrame({'Steel': s_data, 'Cyber': c_data})
    df['Steel_Ret'] = df['Steel'].pct_change()
    df['Cyber_Ret'] = df['Cyber'].pct_change()
    df['Target'] = (df['Cyber_Ret'].shift(-1) > df['Steel_Ret'].shift(-1)).astype(int)
    df['Spread'] = df['Cyber'] / df['Steel']
    df['Momo'] = df['Spread'].pct_change(5)
    df['Vol_Delta'] = df['Cyber_Ret'].rolling(10).std() - df['Steel_Ret'].rolling(10).std()
    df = df.dropna()

    X = df[['Spread', 'Momo', 'Vol_Delta']]
    y = df['Target']
    model = RandomForestClassifier(n_estimators=100, random_state=1111)
    model.fit(X, y)

    latest = X.tail(1)
    return model.predict(latest)[0], model.predict_proba(latest).max(), {
        "Spread": latest['Spread'].values[0],
        "Momo": latest['Momo'].values[0],
        "Vol_Delta": latest['Vol_Delta'].values[0]
    }

# --- MAIN DASHBOARD ---
st.markdown("<h1 style='text-align: center;'>🐍 SOPHIA SERPENT SOFTWARE SOLUTIONS 🐍</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #FFFFFF;'>The Architects of The New World</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00FF41;'>The Future Was Built on Web3</p>", unsafe_allow_html=True)
st.write("---")

# Tactical Asset Inventory
col_k, col_c = st.columns(2)
with col_k:
    st.subheader("KINETIC FRONT (Steel)")
    for name, price in KINETIC_ASSETS.items():
        st.write(f"**{name}:** :red[${price:,.2f}]")

with col_c:
    st.subheader("CYBER FRONT (Silicon)")
    for name, price in CYBER_ASSETS.items():
        st.write(f"**{name}:** :green[${price:,.2f}]")

st.write("---")

if st.button("INITIATE DEEP AUDIT"):
    pred, conf, metrics = run_audit_logic()
    c_gauge, c_brief = st.columns([1, 2])
    st.write(f"Audit Timestamp: {datetime.now().strftime('%H:%M:%S')}")
        
    with c_gauge:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = conf * 100,
            number = {'font': {'color': '#FFFFFF'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickcolor': "#FFFFFF"},
                'bar': {'color': "#00FF41"},
                'bgcolor': "#111111",
                'steps': [
                    {'range': [0, 50], 'color': "#330000"},
                    {'range': [50, 75], 'color': "#333300"},
                    {'range': [75, 100], 'color': "#003300"}]}
        ))
        fig.update_layout(paper_bgcolor='black', font={'color': "white"})
        st.plotly_chart(fig, use_container_width=True)

    with c_brief:
        if pred == 1:
            st.markdown("### SIGNAL: :green[SILICON DOMINANCE]")
            st.write("Digital disruption outpacing physical force. Capital rotation to Cyber recommended.")
        else:
            st.markdown("### SIGNAL: :red[STEEL ESCALATION]")
            st.write("Kinetic force is the market driver. Focus on Prime Contractors.")
        st.metric("CONFIDENCE", f"{conf:.2%}")

    st.write("---")
    st.subheader("Market Telemetry")
    t1, t2, t3 = st.columns(3)
    t1.metric("SPREAD", f"{metrics['Spread']:.4f}")
    t2.metric("MOMENTUM", f"{metrics['Momo']:+.2%}")
    t3.metric("VOL DELTA", f"{metrics['Vol_Delta']:.4f}")

st.write("---")
st.caption("SOPHIA SERPENT SOFTWARE SOLUTIONS | 2026 MARKET INTELLIGENCE HUB")
