// Sophia Serpent Software Solutions
Author: The Architects of The New World : Michael J Scott, Sophia Serpent 
//
import os
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier

# --- CACHE FIX ---
yf.set_tz_cache_location("/tmp")

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
    prediction = model.predict(latest)[0]
    confidence = model.predict_proba(latest).max()
    
    # Extract feature values for the UI
    current_metrics = {
        "Spread": latest['Spread'].values[0],
        "Momo": latest['Momo'].values[0],
        "Vol_Delta": latest['Vol_Delta'].values[0]
    }
    
    return prediction, confidence, current_metrics

# --- UI LAYER ---
st.set_page_config(page_title="LAST DAYS PROTOCOL", layout="wide")
st.title("🛡️ LAST DAYS PROTOCOL: COMMAND CENTER")

if st.button("EXECUTE DEEP AUDIT"):
    pred, conf, metrics = run_audit_logic()
    
    col_gauge, col_briefing = st.columns([1, 2])

    with col_gauge:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = conf * 100,
            title = {'text': "Confidence %"},
            gauge = {'bar': {'color': "#00ff41"}, 'axis': {'range': [0, 100]}}))
        st.plotly_chart(fig, use_container_width=True)
        
    with col_briefing:
        st.subheader("Tactical Briefing")
        status = "SILICON (Cyber)" if pred == 1 else "STEEL (Kinetic)"
        st.metric("CURRENT DOMINANT FRONT", status)
        
        if pred == 1:
            st.warning("Digital disruption is outpacing physical force. Focus: Cybersecurity & AI.")
        else:
            st.error("Kinetic escalation detected. Focus: Prime Contractors & Hardware.")

    st.divider()

    # --- THE CONTEXT PANEL ---
    st.subheader("Metric Intelligence Breakdown")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.write("**Relative Strength (Spread)**")
        st.info(f"Current: {metrics['Spread']:.4f}")
        st.caption("Ratio of Cyber vs. Steel price. A rising number indicates the market favors code over metal.")
        
    with c2:
        st.write("**Trend Velocity (Momentum)**")
        st.info(f"{metrics['Momo']:+.2%}")
        st.caption("5-day speed of the rotation. Positive momentum confirms a shift toward Silicon.")
        
    with c3:
        st.write("**Risk Imbalance (Vol Delta)**")
        st.info(f"{metrics['Vol_Delta']:.4f}")
        st.caption("Difference in sector jitteriness. High delta in Silicon suggests an impending move.")

    st.divider()
    st.write("### 📜 GEOPOLITICAL STATE AUDIT")
    if pred == 1:
        st.write("> **2026 Context:** The conflict has moved to the shadows. Infrastructure protection and data-fusion are the primary value drivers.")
    else:
        st.write("> **2026 Context:** Territorial integrity and physical deterrence are prioritized. Supply chains for munitions and vehicles are under stress.")
