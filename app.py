import streamlit as st
import pandas as pd
import re
from utils.filters import apply_higgons_filter

# === Configuration de la page ===
st.set_page_config(page_title="William Higgons Screener", layout="wide")
st.title("📊 Screener William Higgons")

# === Chargement des données ===
@st.cache_data
def load_data():
    df = pd.read_csv("data/all_results_yfinance_clean.csv")

    # Ajout pays depuis suffixe ticker
    suffix_to_country = {
        ".PA": "France", ".DE": "Allemagne", ".AS": "Pays-Bas",
        ".SW": "Suisse", ".MC": "Espagne", ".MI": "Italie",
        ".L": "Royaume-Uni", ".ST": "Suède", ".CO": "Danemark"
    }
    
    def extract_country(ticker):
        for suffix, country in suffix_to_country.items():
            if ticker.endswith(suffix):
                return country
        return "Autre"

    df["Pays"] = df["Ticker"].apply(extract_country)

    # Appliquer le filtre Higgons
    df["Statut"] = df.apply(lambda row: "✅ Validé" if (row["PER"] < 12 and row["ROE (%)"] > 10 and row["Revenue Growth (%)"] > 0) else "❌ Rejeté", axis=1)

    return df

df = load_data()

# === Affichage ===
st.markdown("### 📋 Aperçu du screening")
st.write("Les entreprises en **vert** passent le filtre William Higgons.")

# Supprimer colonne "Higgons Valid"
df_display = df.drop(columns=["Higgons Valid"], errors='ignore')

# Coloration conditionnelle sans vert (juste rouge)
def color_statut(val):
    return "background-color: #ffcccc" if val == "❌ Rejeté" else ""

# Affichage stylisé
st.dataframe(
    df_display.style.applymap(color_statut, subset=["Statut"]),
    use_container_width=True
)  