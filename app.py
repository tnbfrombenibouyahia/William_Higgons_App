import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

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

    df["Higgons Valid"] = (
        (df["PER"] < 12)
        & (df["ROE (%)"] > 10)
        & (df["Revenue Growth (%)"] > 0)
    )

    suffix_to_country = {
        ".DE": "🇩🇪 Allemagne", ".PA": "🇫🇷 France", ".AS": "🇳🇱 Pays-Bas",
        ".MI": "🇮🇹 Italie", ".SW": "🇨🇭 Suisse", ".L": "🇬🇧 Royaume-Uni",
        ".MC": "🇪🇸 Espagne", ".CO": "🇩🇰 Danemark", ".ST": "🇸🇪 Suède",
        ".BR": "🇧🇪 Belgique", ".OL": "🇳🇴 Norvège", ".IR": "🇮🇪 Irlande",
        ".VI": "🇦🇹 Autriche",
    }

    def detect_country(ticker):
        for suffix, country in suffix_to_country.items():
            if ticker.endswith(suffix):
                return country
        return "❓ Inconnu"

    df["Pays"] = df["Ticker"].apply(detect_country)

    sector_emojis = {
        "Technology": "💻", "Healthcare": "💊", "Financial Services": "💰",
        "Consumer Defensive": "🛒", "Consumer Cyclical": "🧺", "Industrials": "🏗️",
        "Energy": "⛽", "Basic Materials": "⚗️", "Utilities": "🔌",
        "Communication Services": "📡", "Real Estate": "🏠"
    }

    industry_emojis = {
        "Software - Application": "📱", "Semiconductor Equipment & Materials": "🔋",
        "Drug Manufacturers - General": "💉", "Packaged Foods": "🥫",
        "Insurance - Diversified": "🛡️", "Telecom Services": "📞",
        "Specialty Industrial Machinery": "🏭", "Banks - Diversified": "🏦",
        "Life Insurance": "🧬", "Unknown": "❓"
    }

    def with_sector_emoji(row):
        emoji = sector_emojis.get(row["Sector"], "❓")
        return f"{emoji} {row['Sector']}"

    def with_industry_emoji(row):
        emoji = industry_emojis.get(row["Industry"], "🏷️")
        return f"{emoji} {row['Industry']}"

    df["Sector"] = df.apply(with_sector_emoji, axis=1)
    df["Industry"] = df.apply(with_industry_emoji, axis=1)

    df["🧠 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")
    return df

df = load_data()

st.markdown("## 🧰 Filtres")

# Ligne 1 : Pays / Secteur / Industrie
col1, col2, col3 = st.columns(3)
with col1:
    pays_filter = st.selectbox("🌍 Pays", options=[""] + sorted(df["Pays"].unique()))
with col2:
    sector_filter = st.selectbox("🏷️ Secteur", options=[""] + sorted(df["Sector"].unique()))
with col3:
    industry_filter = st.selectbox("🏭 Industrie", options=[""] + sorted(df["Industry"].unique()))

# Ligne 2 : PER / ROE / Croissance
col4, col5, col6 = st.columns(3)
with col4:
    per_min, per_max = st.slider("💰 PER", 0.0, 100.0, (0.0, 100.0))
with col5:
    roe_min = st.slider("📈 ROE (%) minimum", 0.0, 100.0, 0.0)
with col6:
    growth_min = st.slider("📊 Croissance min. (%)", -50.0, 100.0, 0.0)

# Ligne 3 : Ticker + Filtrage mode
# Ligne 3 : Ticker + Filtrage mode
col7, col8 = st.columns([3, 1])
with col7:
    search_ticker = st.text_input("🔎 Rechercher un ticker", "")
with col8:
    filtrage_mode = st.selectbox("🎯 Affichage", ["🇪🇺 Toutes les entreprises", "🤴 Screening uniquement"])

# === Application des filtres ===
df_filtered = df.copy()

if search_ticker:
    df_filtered = df_filtered[df_filtered["Ticker"].str.contains(search_ticker.upper())]
if pays_filter:
    df_filtered = df_filtered[df_filtered["Pays"] == pays_filter]
if sector_filter:
    df_filtered = df_filtered[df_filtered["Sector"] == sector_filter]
if industry_filter:
    df_filtered = df_filtered[df_filtered["Industry"] == industry_filter]

df_filtered = df_filtered[
    (df_filtered["PER"] >= per_min) & (df_filtered["PER"] <= per_max) &
    (df_filtered["ROE (%)"] >= roe_min) &
    (df_filtered["Revenue Growth (%)"] >= growth_min)
]

if filtrage_mode == "🤴 Screening uniquement":
    df_filtered = df_filtered[df_filtered["🧠 Statut"] == "✅ Validé"]

# === Score Higgons ===
def compute_higgons_score(row):
    if not row["Higgons Valid"]:
        return np.nan
    score = 0
    per = row["PER"]
    if per < 8: score += 35
    elif per < 10: score += 25
    elif per < 12: score += 15
    elif per < 15: score += 5

    roe = row["ROE (%)"]
    if roe > 20: score += 35
    elif roe > 15: score += 25
    elif roe > 10: score += 15
    elif roe > 5: score += 5

    growth = row["Revenue Growth (%)"]
    if growth > 15: score += 20
    elif growth > 10: score += 15
    elif growth > 5: score += 10
    elif growth > 0: score += 5

    defensives = ["Healthcare", "Consumer Defensive"]
    if any(sec in row["Sector"] for sec in defensives):
        score += 10
    return score

df_filtered["🎯 Score Higgons"] = df_filtered.apply(compute_higgons_score, axis=1)
df_filtered["🎯 Score Higgons Texte"] = df_filtered["🎯 Score Higgons"].apply(
    lambda x: "— Rejeté" if pd.isna(x) else int(x)
)

# === Tableau final ===
df_display = df_filtered.drop(columns=["Higgons Valid", "🎯 Score Higgons"])
df_display = df_display.rename(columns={
    "Price": "💰 Cours de l'action (€)",
    "EPS": "📊 Bénéfice par action (EPS)",
    "PER": "📉 Price Earning Ratio (PER)",
    "ROE (%)": "🏦 Rentabilité des fonds propres (%)",
    "Revenue Growth (%)": "📈 Croissance du chiffre d'affaires (%)",
    "Sector": "🏷️ Secteur",
    "Industry": "🏭 Industrie",
    "Pays": "🌍 Pays",
    "🧠 Statut": "✅ Filtre William Higgons",
    "🎯 Score Higgons Texte": "🎯 Score Higgons (sur 100)"
})

st.dataframe(df_display, use_container_width=True)

# === Analyse individuelle ===
st.markdown("---")
st.subheader("📊 Analyse individuelle")

if not df_display.empty:
    selected_ticker = st.text_input(
        "🔍 Entrer un ticker pour afficher son graphique :",
        value=df_display["Ticker"].iloc[0] if not df_display.empty else ""
    )

    if selected_ticker:
        stock = yf.Ticker(selected_ticker)
        with st.spinner("Chargement des données..."):
            hist = stock.history(period="max")
        if hist.empty:
            st.warning("Données historiques indisponibles pour ce ticker.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Cours de clôture"))
            fig.update_layout(
                title=f"📈 Évolution historique de {selected_ticker}",
                xaxis_title="Date",
                yaxis_title="Prix (€)",
                template="plotly_dark",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

# === Date de mise à jour ===
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        last_update = f.read().strip()
    st.info(f"🕒 Dernière mise à jour automatique des données : `{last_update}`")
except FileNotFoundError:
    st.warning("⚠️ Aucune mise à jour automatique détectée.")