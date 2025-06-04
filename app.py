import streamlit as st
import pandas as pd
import os

# === Configuration de la page ===
st.set_page_config(page_title="William Higgons Screener", layout="wide")
st.title("📊 Screener William Higgons")
st.markdown("### 🧾 Aperçu du screening")
st.write("Les entreprises en **vert** passent le filtre William Higgons.")

# === Chargement des données ===
@st.cache_data
def load_data():
    df = pd.read_csv("data/all_results_yfinance_clean.csv")

    # Statut booléen du filtre Higgons
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
        ".OL": "🇳🇴 Norvège",
        ".BR": "🇧🇪 Belgique",
        ".VI": "🇦🇹 Autriche",
    }

    def detect_country(ticker):
        for suffix, country in suffix_to_country.items():
            if ticker.endswith(suffix):
                return country
        return "❓ Inconnu"

    df["Pays"] = df["Ticker"].apply(detect_country)

    # Colonnes affichées
    colonnes = [
        "Ticker", "Pays", "Price", "EPS", "PER", "ROE (%)", "Revenue Growth (%)"
    ]
    if "Sector" in df.columns:
        colonnes.append("Sector")

    # Statut visuel
    df["🧠 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")

    return df[colonnes + ["🧠 Statut"]]

# === Affichage principal ===
df_display = load_data()
st.dataframe(df_display, use_container_width=True)

# === Date de mise à jour ===
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        last_update = f.read().strip()
    st.info(f"🕒 Dernière mise à jour automatique des données : `{last_update}`")
except FileNotFoundError:
    st.warning("❌ Aucune mise à jour automatique enregistrée.")