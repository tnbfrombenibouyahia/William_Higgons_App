import streamlit as st
import pandas as pd
from datetime import datetime

# === Configuration de la page ===
st.set_page_config(page_title="William Higgons Screener", layout="wide")
st.title("👨‍🌾 Screener William Higgons")
st.markdown("### 🧾 Aperçu du screening")
st.write("Ce screener analyse les entreprises selon les critères de William Higgons.")

# === Chargement des données ===
@st.cache_data
def load_data():
    df = pd.read_csv("data/all_results_yfinance_clean.csv")

    # Ajout du statut booléen
    df["Higgons Valid"] = (
        (df["PER"] < 12)
        & (df["ROE (%)"] > 10)
        & (df["Revenue Growth (%)"] > 0)
    )

    # Mapping des suffixes vers pays
    suffix_to_country = {
        ".DE": "🇩🇪 Allemagne",
        ".PA": "🇫🇷 France",
        ".AS": "🇳🇱 Pays-Bas",
        ".MI": "🇮🇹 Italie",
        ".SW": "🇨🇭 Suisse",
        ".L": "🇬🇧 Royaume-Uni",
        ".MC": "🇪🇸 Espagne",
        ".CO": "🇩🇰 Danemark",
        ".ST": "🇸🇪 Suède",
    }

    def detect_country(ticker):
        for suffix, country in suffix_to_country.items():
            if ticker.endswith(suffix):
                return country
        return "❓ Inconnu"

    df["Pays"] = df["Ticker"].apply(detect_country)
    return df

df = load_data()

# Ajout de la colonne d'affichage
df["🧠 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")

# Suppression de la colonne booléenne
df_display = df.drop(columns=["Higgons Valid"])

# === Affichage Streamlit ===
st.dataframe(df_display, use_container_width=True)

# === Affichage date mise à jour automatique ===
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        last_update = f.read().strip()
    st.info(f"🕒 Dernière mise à jour automatique des données : `{last_update}`")
except FileNotFoundError:
    st.warning("❌ Aucune mise à jour automatique enregistrée.")