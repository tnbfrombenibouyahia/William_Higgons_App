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

    # Colonne de statut booléen Higgons
    df["Higgons Valid"] = (
        (df["PER"] < 12) &
        (df["ROE (%)"] > 10) &
        (df["Revenue Growth (%)"] > 0)
    )

    # Mapping suffixe → pays
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

    # Ajout émojis secteur
    sector_emojis = {
        "Technology": "💻", "Healthcare": "💊", "Financial Services": "💰",
        "Consumer Defensive": "🛒", "Industrials": "🏭", "Utilities": "🔌",
        "Basic Materials": "⚙️", "Energy": "🛢️", "Real Estate": "🏠",
        "Consumer Cyclical": "🎯", "Communication Services": "📡"
    }

    df["Sector"] = df["Sector"].apply(lambda x: f"{sector_emojis.get(x, '📂')} {x}")

    # Ajout émojis industrie
    industry_emojis = {
        "Software – Application": "🧩", "Drug Manufacturers – General": "💊",
        "Semiconductor Equipment & Materials": "🔋",
        "Packaged Foods": "🥫", "Insurance – Diversified": "🛡️",
        "Banks – Regional": "🏦", "Life Insurance": "🧬",
        "Utilities – Regulated Electric": "🔌",
        "Oil & Gas Integrated": "⛽", "Apparel Retail": "👕"
    }

    df["Industry"] = df["Industry"].apply(lambda x: f"{industry_emojis.get(x, '🏷️')} {x}")

    # Colonne statut visuel
    df["🧠 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")

    return df

df = load_data()

# === 🎛️ Filtres dynamiques ===
st.sidebar.title("🎛️ Filtres")
pays = st.sidebar.multiselect("🌍 Pays", options=sorted(df["Pays"].unique()), default=None)
secteurs = st.sidebar.multiselect("🏢 Secteur", options=sorted(df["Sector"].unique()), default=None)
industries = st.sidebar.multiselect("🏷️ Industrie", options=sorted(df["Industry"].unique()), default=None)

per_min, per_max = st.sidebar.slider("💰 PER", 0.0, 100.0, (0.0, 100.0))
roe_min = st.sidebar.slider("📈 ROE (%) minimum", 0.0, 100.0, 0.0)
growth_min = st.sidebar.slider("📊 Croissance min. (%)", -50.0, 100.0, 0.0)

valid_only = st.sidebar.checkbox("✅ Seulement les sociétés validées")

# === 📄 Application des filtres ===
df_filtered = df.copy()
if pays:
    df_filtered = df_filtered[df_filtered["Pays"].isin(pays)]
if secteurs:
    df_filtered = df_filtered[df_filtered["Sector"].isin(secteurs)]
if industries:
    df_filtered = df_filtered[df_filtered["Industry"].isin(industries)]

df_filtered = df_filtered[
    (df_filtered["PER"] >= per_min) & (df_filtered["PER"] <= per_max) &
    (df_filtered["ROE (%)"] >= roe_min) &
    (df_filtered["Revenue Growth (%)"] >= growth_min)
]

if valid_only:
    df_filtered = df_filtered[df_filtered["Higgons Valid"] == True]

# Suppression de la colonne booléenne
df_display = df_filtered.drop(columns=["Higgons Valid"])

# === 🖥️ Affichage tableau final ===
st.dataframe(df_display, use_container_width=True)

# === 📆 Date de mise à jour ===
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        last_update = f.read().strip()
    st.info(f"🕒 Dernière mise à jour automatique des données : `{last_update}`")
except FileNotFoundError:
    st.warning("❌ Aucune mise à jour automatique enregistrée.")