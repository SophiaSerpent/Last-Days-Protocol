
import os
import yfinance as yf

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import logging
import streamlit as st
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# --- SYSTEM CONFIGURATION ---
warnings.filterwarnings('ignore')
logging.basicConfig(filename='protocol_audit.log', level=logging.INFO, format='%(asctime)s | %(message)s')

# --- BACKEND: LAST DAYS LOGIC ---
def run_audit_logic():
    steel_tickers = ["LMT", "RTX", "NOC", "GD", "BA"]
    cyber_tickers = ["CRWD", "PANW", "PLTR", "FTNT", "CACI"]
   
    try:
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
       
        status = "SILICON" if prediction == 1 else "STEEL"
        msg = f"STATUS: {status} | CONFIDENCE: {confidence:.2%}"
        logging.info(msg)
        return prediction, confidence, msg
    except Exception as e:
        return None, 0, f"Error: {e}"

# --- FRONTEND: COMMAND CENTER UI ---
st.set_page_config(page_title="LAST DAYS PROTOCOL", layout="wide")
st.title("🛡️ LAST DAYS PROTOCOL: COMMAND CENTER")

if st.button("EXECUTE DEEP AUDIT"):
    pred, conf, report = run_audit_logic()
   
    col1, col2 = st.columns([1, 1])
    with col1:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = conf * 100,
            title = {'text': "Confidence %"},
            gauge = {'bar': {'color': "#00ff41"}, 'axis': {'range': [0, 100]}}))
        st.plotly_chart(fig)
    with col2:
        st.metric("FRONTLINE", "SILICON (CYBER)" if pred == 1 else "STEEL (KINETIC)")
        st.success(report)

st.divider()
st.write("### 📜 AUDIT LOG")
try:
    with open('protocol_audit.log', 'r') as f:
        for line in reversed(f.readlines()[-5:]): st.text(line.strip())
except: st.info("Initializing first log entry...")
