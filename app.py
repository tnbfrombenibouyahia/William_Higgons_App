import streamlit as st
import pandas as pd
from datetime import datetime

# === Config ===
st.set_page_config(page_title="Screener William Higgons", layout="wide")
st.title("👨‍🌾 Screener William Higgons")
st.markdown("Filtre les entreprises du Stoxx600 selon les critères Higgons : PER < 12, ROE > 10%, Chiffre d'affaires en croissance.")

# === Chargement des données ===
@st.cache_data

def load_data():
    df = pd.read_csv("data/all_results_yfinance_clean.csv")

    # Drapeau Higgons
    df["Higgons Valid"] = (
        (df["PER"] < 12)
        & (df["ROE (%)"] > 10)
        & (df["Revenue Growth (%)"] > 0)
    )

    # Pays
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
    df["Pays"] = df["Ticker"].apply(lambda t: next((country for suffix, country in suffix_to_country.items() if t.endswith(suffix)), "❓ Inconnu"))

    # Emoji pour secteur
    sector_emojis = {
        "Technology": "💻", "Consumer Defensive": "🍬",
        "Healthcare": "💉", "Financial Services": "💰",
        "Industrials": "💼", "Basic Materials": "🏫",
        "Energy": "⛽", "Utilities": "🔦",
        "Real Estate": "🏠", "Communication Services": "📱"
    }
    df["Secteur"] = df["Sector"].apply(lambda s: f"{sector_emojis.get(s, '')} {s}" if pd.notna(s) else "")
    df["Industrie"] = df["Industry"].apply(lambda i: f"🔢 {i}" if pd.notna(i) else "")

    df["🧠 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")
    return df

df = load_data()

# === Filtres ===
st.sidebar.header("🔧 Filtres")

# Pays
pays = st.sidebar.multiselect("🌐 Pays", options=sorted(df["Pays"].unique()), default=None)
if pays:
    df = df[df["Pays"].isin(pays)]

# Secteur
secteurs = st.sidebar.multiselect("🌍 Secteurs", options=sorted(df["Secteur"].dropna().unique()))
if secteurs:
    df = df[df["Secteur"].isin(secteurs)]

# Industrie
industries = st.sidebar.multiselect("💼 Industries", options=sorted(df["Industrie"].dropna().unique()))
if industries:
    df = df[df["Industrie"].isin(industries)]

# Critères numériques
per_min, per_max = st.sidebar.slider("PER", 0.0, 30.0, (0.0, 12.0))
roe_min = st.sidebar.slider("ROE (%) minimum", 0.0, 50.0, 10.0)
growth_min = st.sidebar.slider("Croissance du CA (%) minimum", -50.0, 100.0, 0.0)

# Statut Higgons
statut = st.sidebar.selectbox("🧪 Statut Higgons", ["Tous", "✅ Validé", "❌ Rejeté"])

# Application des filtres
filtres = (
    (df["PER"] >= per_min) & (df["PER"] <= per_max) &
    (df["ROE (%)"] >= roe_min) &
    (df["Revenue Growth (%)"] >= growth_min)
)
if statut != "Tous":
    filtres &= df["🧠 Statut"] == statut

df_filtered = df[filtres].copy()

# Affichage tableau
st.dataframe(
    df_filtered[
        ["Ticker", "Prix", "EPS", "PER", "ROE (%)", "Revenue Growth (%)", "🧠 Statut", "Pays", "Secteur", "Industrie"]
    ].sort_values(by="PER"),
    use_container_width=True,
)

# Export CSV
st.download_button("📂 Exporter les résultats filtrés", data=df_filtered.to_csv(index=False).encode("utf-8"), file_name="higgons_filtered.csv", mime="text/csv")

# Dernier update
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        st.info(f"🕒 Données mises à jour le `{f.read().strip()}`")
except FileNotFoundError:
    st.warning("❌ Aucune mise à jour enregistrée.")
