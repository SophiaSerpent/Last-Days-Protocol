import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier

# --- CACHE FIX & UI CONFIG ---
yf.set_tz_cache_location("/tmp")
st.set_page_config(page_title="LAST DAYS PROTOCOL", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS: THE "DEEP BLACK" UI INJECTION ---
st.markdown("""
    <style>
    /* Main Background and Sidebar */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }
    
    /* Text Colors */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #FFFFFF !important;
        font-family: 'Courier New', Courier, monospace;
    }

    /* Metric Tactical Colors */
    [data-testid="stMetricValue"] { color: #00FF41 !important; } /* Matrix Green */
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    
    /* Button Style */
    div.stButton > button:first-child {
        background-color: #000000;
        color: #00FF41;
        border: 2px solid #00FF41;
        border-radius: 0px;
        width: 100%;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #00FF41;
        color: #000000;
    }

    /* Info/Warning/Error boxes */
    .stAlert {
        background-color: #000000 !important;
        border: 1px solid #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND LOGIC ---
def run_audit_logic():
    steel_tickers = ["LMT", "RTX", "NOC", "GD", "BA"]
    cyber_tickers = ["CRWD", "PANW", "PLTR", "FTNT", "CACI"]
    
    s_data = yf.download(steel_tickers, period="2y", interval="1d", progress=False)['Close'].mean(axis=1)
    c_data = yf.download(cyber_tickers, period="2y", interval="1d", progress=False)['Close'].mean(axis=1)
    
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

# --- COMMAND CENTER UI ---
st.title("🛡️ LAST DAYS PROTOCOL")
st.write("---")

if st.button("INITIATE DEEP AUDIT"):
    pred, conf, metrics = run_audit_logic()
    
    col_gauge, col_brief = st.columns([1, 2])
    
    with col_gauge:
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

    with col_brief:
        # Tactical Signal Logic
        if pred == 1:
            st.markdown("### SIGNAL: :green[SILICON DOMINANCE]")
            st.write("The digital front is accelerating. Capital rotation to Cyber recommended.")
        else:
            st.markdown("### SIGNAL: :red[STEEL ESCALATION]")
            st.write("Kinetic force is the market driver. Hold positions in Prime Contractors.")
        
        st.metric("CONFIDENCE", f"{conf:.2%}")

    st.write("---")
    st.subheader("Frontline Telemetry")
    c1, c2, c3 = st.columns(3)
    c1.metric("SPREAD", f"{metrics['Spread']:.4f}")
    c2.metric("MOMENTUM", f"{metrics['Momo']:+.2%}")
    c3.metric("VOL DELTA", f"{metrics['Vol_Delta']:.4f}")

st.write("---")
st.caption("2026 ENIVITROL-19 SECURITY SUPER-CYCLE | MAESTRO UNIVERSITY AUDITED")


