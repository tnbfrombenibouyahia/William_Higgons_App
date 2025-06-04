import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import os

# === Configuration ===
st.set_page_config(page_title="William Higgons Screener", layout="wide")
st.title("📊 Screener William Higgons")
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

    # Pays
    suffix_to_country = {
        ".DE": "🇩🇪 Allemagne", ".PA": "🇫🇷 France", ".AS": "🇳🇱 Pays-Bas",
        ".MI": "🇮🇹 Italie", ".SW": "🇨🇭 Suisse", ".L": "🇬🇧 Royaume-Uni",
        ".MC": "🇪🇸 Espagne", ".CO": "🇩🇰 Danemark", ".ST": "🇸🇪 Suède",
        ".BR": "🇧🇪 Belgique", ".OL": "🇳🇴 Norvège", ".IR": "🇮🇪 Irlande",
        ".VI": "🇦🇹 Autriche"
    }

    def detect_country(ticker):
        for suffix, country in suffix_to_country.items():
            if ticker.endswith(suffix):
                return country
        return "❓ Inconnu"

    df["Pays"] = df["Ticker"].apply(detect_country)

    # Emojis secteurs/industries
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

    df["Sector"] = df.apply(lambda row: f"{sector_emojis.get(row['Sector'], '❓')} {row['Sector']}", axis=1)
    df["Industry"] = df.apply(lambda row: f"{industry_emojis.get(row['Industry'], '🏷️')} {row['Industry']}", axis=1)

    df["🧠 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")
    return df

df = load_data()

# === Filtres ===
st.sidebar.header("🧰 Filtres")
search_ticker = st.sidebar.text_input("🔎 Rechercher un ticker", "")

pays_filter = st.sidebar.selectbox("🌍 Pays", options=[""] + sorted(df["Pays"].unique()))
sector_filter = st.sidebar.selectbox("🏷️ Secteur", options=[""] + sorted(df["Sector"].unique()))
industry_filter = st.sidebar.selectbox("🏭 Industrie", options=[""] + sorted(df["Industry"].unique()))

per_min, per_max = st.sidebar.slider("💰 PER", 0.0, 100.0, (0.0, 100.0))
roe_min = st.sidebar.slider("📈 ROE (%) minimum", 0.0, 100.0, 0.0)
growth_min = st.sidebar.slider("📊 Croissance min. (%)", -50.0, 100.0, 0.0)

only_higgons = st.sidebar.checkbox("✅ Seulement les sociétés validées")

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

if only_higgons:
    df_filtered = df_filtered[df_filtered["🧠 Statut"] == "✅ Validé"]

# === Affichage principal ===
df_display = df_filtered.drop(columns=["Higgons Valid"])
st.dataframe(df_display, use_container_width=True)

# === Date mise à jour
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        last_update = f.read().strip()
    st.info(f"🕒 Dernière mise à jour automatique des données : `{last_update}`")
except FileNotFoundError:
    st.warning("⚠️ Aucune mise à jour automatique détectée.")

# === Analyse individuelle ===
if not df_display.empty:
    st.markdown("---")
    st.subheader("📊 Analyse individuelle")

    selected_ticker = st.selectbox(
        "Sélectionner une entreprise pour voir son graphique :",
        df_display["Ticker"].unique()
    )

    stock = yf.Ticker(selected_ticker)
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

    info = stock.info
    st.markdown("### 🧾 Fiche signalétique")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Nom", info.get("shortName", "N/A"))
        st.metric("Prix actuel", f'{info.get("currentPrice", "N/A")} {info.get("currency", "")}')
        st.metric("PER", round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A")
        st.metric("Capitalisation", f'{round(info.get("marketCap", 0)/1e9, 2)} B' if info.get("marketCap") else "N/A")

    with col2:
        st.metric("Secteur", info.get("sector", "N/A"))
        st.metric("Industrie", info.get("industry", "N/A"))
        st.metric("Dividende (%)", info.get("dividendYield", "N/A"))
        st.metric("Beta", info.get("beta", "N/A"))
else:
    st.warning("Aucune entreprise à afficher pour l’analyse individuelle.")