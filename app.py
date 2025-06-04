import streamlit as st
import pandas as pd

# === Configuration de la page ===
st.set_page_config(page_title="William Higgons Screener", layout="wide")
st.title("📊 Screener William Higgons")
st.markdown("### 🧾 Aperçu du screening")
st.write("Les entreprises en **vert** passent le filtre William Higgons.")

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

# Ajout de la colonne d'affichage avec emoji
df["🧠 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")

# Suppression de la colonne booléenne
df_display = df.drop(columns=["Higgons Valid"])

# === Affichage tableau sans couleurs ===
st.dataframe(df_display, use_container_width=True)