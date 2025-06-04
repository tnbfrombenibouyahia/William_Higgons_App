import streamlit as st
import pandas as pd
import os
import yfinance as yf
import plotly.graph_objects as go

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

    # === Emojis pour les secteurs et industries
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
        "Software - Application": "📱",
        "Semiconductor Equipment & Materials": "🔋",
        "Drug Manufacturers - General": "💉",
        "Packaged Foods": "🥫",
        "Insurance - Diversified": "🛡️",
        "Telecom Services": "📞",
        "Specialty Industrial Machinery": "🏭",
        "Banks - Diversified": "🏦",
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

    # Ajout du statut
    df["🧠 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")
    return df

df = load_data()

# === Barre latérale de filtre ===
st.sidebar.header("🧰 Filtres")

# Recherche par Ticker
search_ticker = st.sidebar.text_input("🔎 Rechercher un ticker", "")

# Filtres dynamiques
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

# Suppression colonne bool
df_display = df_filtered.drop(columns=["Higgons Valid"])

# === Affichage final
st.dataframe(df_display, use_container_width=True)

# === 🔎 Zoom sur une société ===
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
            # 📈 Données historiques
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


# === 📅 Date de dernière mise à jour (juste après l'analyse)
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        last_update = f.read().strip()
    st.info(f"🕒 Dernière mise à jour automatique des données : `{last_update}`")
except FileNotFoundError:
    st.warning("⚠️ Aucune mise à jour automatique détectée.")