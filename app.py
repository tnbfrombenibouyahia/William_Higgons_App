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

    # Statut booléen Higgons
    df["Higgons Valid"] = (
        (df["PER"] < 12)
        & (df["ROE (%)"] > 10)
        & (df["Revenue Growth (%)"] > 0)
    )

    # === Ajout du pays ===
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
        ".BR": "🇧🇪 Belgique",
        ".OL": "🇳🇴 Norvège",
        ".VI": "🇦🇹 Autriche",
    }

    def detect_country(ticker):
        for suffix, country in suffix_to_country.items():
            if ticker.endswith(suffix):
                return country
        return "❓ Inconnu"

    df["Pays"] = df["Ticker"].apply(detect_country)

    # === Ajout d'émojis pour Sector ===
    sector_emojis = {
        "Technology": "💻 Technology",
        "Healthcare": "🧬 Healthcare",
        "Financial Services": "💰 Financial Services",
        "Consumer Defensive": "🛒 Consumer Defensive",
        "Consumer Cyclical": "🛍️ Consumer Cyclical",
        "Communication Services": "📡 Communication Services",
        "Industrials": "🏭 Industrials",
        "Energy": "⚡ Energy",
        "Utilities": "🔌 Utilities",
        "Real Estate": "🏘️ Real Estate",
        "Basic Materials": "🧱 Basic Materials"
    }

    df["Sector"] = df["Sector"].apply(lambda x: sector_emojis.get(x, f"❓ {x}"))

    # === Ajout d'émojis pour Industry ===
    industry_emojis = {
        "Software - Application": "📱 Software",
        "Drug Manufacturers - General": "💊 Pharma",
        "Semiconductor Equipment & Materials": "🔩 Semiconductors",
        "Packaged Foods": "🥫 Packaged Foods",
        "Banks - Regional": "🏦 Regional Banks",
        "Insurance - Life": "🛡️ Life Insurance",
        "Utilities - Renewable": "🌱 Renewable Energy"
    }

    df["Industry"] = df["Industry"].apply(lambda x: industry_emojis.get(x, f"❓ {x}"))

    return df

# === Chargement des données ===
df = load_data()

# 🧠 Affichage du statut
df["🧠 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")

# Suppression de la colonne booléenne
df_display = df.drop(columns=["Higgons Valid"])

# Ordre des colonnes (optionnel)
colonnes = ["Ticker", "Pays", "Sector", "Industry", "Price", "EPS", "PER", "ROE (%)", "Revenue Growth (%)", "🧠 Statut"]
df_display = df_display[[col for col in colonnes if col in df_display.columns]]

# === Affichage principal ===
st.dataframe(df_display, use_container_width=True)

# === Dernière mise à jour ===
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        last_update = f.read().strip()
    st.info(f"🕒 Dernière mise à jour automatique des données : `{last_update}`")
except FileNotFoundError:
    st.warning("❌ Aucune mise à jour automatique enregistrée.")