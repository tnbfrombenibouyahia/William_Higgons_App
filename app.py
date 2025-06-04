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
        ".SW": "🇨🇭 Suisse",
        ".L": "🇬🇧 Royaume-Uni",
        ".MC": "🇪🇸 Espagne",
        ".CO": "🇩🇰 Danemark",
        ".ST": "🇸🇪 Suède",
        ".BR": "🇧🇪 Belgique",
        ".OL": "🇳🇴 Norvège",
        ".IR": "🇮🇪 Irlande",
        ".VI": "🇦🇹 Autriche",
    }

    def detect_country(ticker):
        for suffix, country in suffix_to_country.items():
            if ticker.endswith(suffix):
                return country
        return "❓ Inconnu"

    df["Pays"] = df["Ticker"].apply(detect_country)

    # === Mapping des émojis secteur
    sector_emojis = {
        "Technology": "💻",
        "Healthcare": "💊",
        "Financial Services": "💰",
        "Consumer Defensive": "🛒",
        "Consumer Cyclical": "🧺",
        "Industrials": "🏗️",
        "Energy": "⛽",
        "Basic Materials": "⚗️",
        "Utilities": "🔌",
        "Communication Services": "📡",
        "Real Estate": "🏠"
    }

    industry_emojis = {
        "Software—Application": "📱",
        "Semiconductor Equipment & Materials": "🔋",
        "Drug Manufacturers—General": "💉",
        "Packaged Foods": "🥫",
        "Insurance—Diversified": "🛡️",
        "Utilities—Regulated Electric": "⚡",
        "Apparel Retail": "👕",
        "Banks—Regional": "🏦",
        "Life Insurance": "🧬",
        "Unknown": "❓"
    }

    def with_sector_emoji(row):
        emoji = sector_emojis.get(row["Sector"], "❓")
        return f"{emoji} {row['Sector']}"

    def with_industry_emoji(row):
        emoji = industry_emojis.get(row["Industry"], "🏷️")
        return f"{emoji} {row['Industry']}"

    df["Sector"] = df.apply(with_sector_emoji, axis=1)
    df["Industry"] = df.apply(with_industry_emoji, axis=1)

    return df

df = load_data()

# === Création de la colonne statut
df["🧠 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")
df_display = df.drop(columns=["Higgons Valid"])

# === 🔍 Barre de recherche par Ticker ===
st.sidebar.markdown("## 🔍 Recherche")
search_query = st.sidebar.text_input("Rechercher un ticker (ex: ASML, SAP, TTE)", "")
if search_query:
    df_display = df_display[df_display["Ticker"].str.contains(search_query.upper())]

# === Affichage tableau final
st.dataframe(df_display, use_container_width=True)

# === ⏰ Date de mise à jour automatique
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        last_update = f.read().strip()
    st.info(f"🕒 Dernière mise à jour automatique des données : `{last_update}`")
except FileNotFoundError:
    st.warning("⚠️ Aucune mise à jour automatique détectée.")