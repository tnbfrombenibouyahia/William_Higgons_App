import streamlit as st
import pandas as pd
import os
import yfinance as yf
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from st_aggrid import AgGrid, GridOptionsBuilder

# === Configuration de la page ===
st.set_page_config(page_title="William Higgons Screener", layout="wide")
st.title("📊 Screener William Higgons")

# 🎥 Vidéo de présentation
st.markdown("### 🎥 William Higgons explique sa stratégie")
st.video("https://www.youtube.com/watch?v=Ct3ZDvUjCFI")

st.markdown("### 🧾 Aperçu du screening")
st.write("Les entreprises en **vert** passent le filtre William Higgons.")

# === Chargement des données ===
@st.cache_data
def load_data():
    df = pd.read_csv("data/all_results_yfinance_clean.csv")

    # Ajout colonne Higgons
    df["Higgons Valid"] = (
        (df["PER"] < 12)
        & (df["ROE (%)"] > 10)
        & (df["Revenue Growth (%)"] > 0)
    )

    # === Ajout du pays
    suffix_to_country = {
        ".DE": "🇩🇪 Allemagne",
        ".PA": "🇫🇷 France",
        ".AS": "🇳🇱 Pays-Bas",
        ".MI": "🇮🇹 Italie",