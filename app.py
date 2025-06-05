import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# === Configuration de la page ===
st.set_page_config(page_title="William Higgons Screener", layout="wide")
st.title("📊 Screener William Higgons")
with st.expander("ℹ️ À propos de cette application", expanded=True):
    st.markdown("""
    Cette application est un **screener d'actions européennes** inspiré de la méthode de sélection de William Higgons, gérant chez Indépendance & Expansion.

    ### 🎥 Interview de William Higgons
    """)
    st.video("https://www.youtube.com/watch?v=Ct3ZDvUjCFI")
    st.markdown("""
    ---
    ### 🎯 Objectif
    Identifier des entreprises sous-évaluées avec :
    - **PER < 12** : valorisation attractive.
    - **ROE > 10%** : rentabilité élevée des fonds propres.
    - **Croissance du chiffre d’affaires > 0%** : dynamique de croissance.

    ### 🧠 Filtrage
    Les entreprises qui remplissent ces trois critères sont marquées comme **"✅ Validé"** dans le filtre William Higgons.

    ### 📊 Score Higgons (/100)
    Pour affiner la sélection, un **score pondéré** est attribué à chaque société validée :
    - Jusqu’à **35 pts pour un PER très faible**.
    - Jusqu’à **35 pts pour un ROE élevé**.
    - Jusqu’à **20 pts pour une croissance forte**.
    - **+10 pts** de bonus si la société appartient à un **secteur défensif** (*Healthcare, Consumer Defensive*).

    ### 📈 Analyse individuelle
    En bas de page, tu peux consulter l’évolution historique du cours d’une entreprise sélectionnée.

    ---
    > Données récupérées depuis **Yahoo Finance** via `yfinance`.  
    > Mises à jour régulières automatiquement 📅
    """)

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

    df["🧠 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")

    return df

df = load_data()

# === 🎯 Score Higgons (pondéré)
def compute_higgons_score(row):
    if not row["Higgons Valid"]:
        return None

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

    # Bonus secteur défensif
    defensives = ["Healthcare", "Consumer Defensive"]
    if any(d in str(row["Sector"]) for d in defensives):
        score += 10

    return score

df["🎯 Score Higgons"] = df.apply(compute_higgons_score, axis=1)
df["🎯 Score Higgons Texte"] = df["🎯 Score Higgons"].apply(lambda x: "— Rejeté" if pd.isna(x) else int(x))

# === Barre latérale de filtres ===
st.sidebar.header("🧰 Filtres")

search_ticker = st.sidebar.text_input("🔎 Rechercher un ticker", "")
pays_filter = st.sidebar.selectbox("🌍 Pays", [""] + sorted(df["Pays"].unique()))
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

df_filtered = df_filtered[
    (df_filtered["PER"] >= per_min) & (df_filtered["PER"] <= per_max) &
    (df_filtered["ROE (%)"] >= roe_min) &
    (df_filtered["Revenue Growth (%)"] >= growth_min)
]

if only_higgons:
    df_filtered = df_filtered[df_filtered["🧠 Statut"] == "✅ Validé"]

# === Renommage des colonnes
df_display = df_filtered.rename(columns={
    "Price": "💶 Cours (€)",
    "EPS": "📊 Bénéfice par action",
    "PER": "📉 PER (Cours / Bénéfices)",
    "ROE (%)": "🏦 Rendement des fonds propres (%)",
    "Revenue Growth (%)": "📈 Croissance du chiffre d'affaires (%)",
    "Pays": "🌍 Pays",
    "🧠 Statut": "✅ Filtre William Higgons",
    "🎯 Score Higgons Texte": "🎯 Score William Higgons (/100)"
})

# === Affichage principal
st.dataframe(
    df_display[[
        "Ticker", "💶 Cours (€)", "📊 Bénéfice par action", "📉 PER (Cours / Bénéfices)",
        "🏦 Rendement des fonds propres (%)", "📈 Croissance du chiffre d'affaires (%)",
        "🌍 Pays", "✅ Filtre William Higgons", "🎯 Score William Higgons (/100)"
    ]],
    use_container_width=True
)

# === Analyse individuelle
st.markdown("---")
st.subheader("📊 Analyse individuelle")

if not df_display.empty:
    selected_ticker = st.text_input(
        "🔍 Entrer un ticker pour afficher son graphique :",
        value=df_display["Ticker"].iloc[0]
    )

    if selected_ticker:
        stock = yf.Ticker(selected_ticker)
        with st.spinner("Chargement des données..."):
            hist = stock.history(period="max")
        if hist.empty:
            st.warning("Données historiques indisponibles.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Cours de clôture"))
            fig.update_layout(
                title=f"📈 Évolution historique de {selected_ticker}",
                xaxis_title="Date", yaxis_title="Prix (€)",
                template="plotly_dark", height=500
            )
            st.plotly_chart(fig, use_container_width=True)

# === Dernière mise à jour
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        last_update = f.read().strip()
    st.info(f"🕒 Dernière mise à jour automatique des données : `{last_update}`")
except FileNotFoundError:
    st.warning("⚠️ Aucune mise à jour automatique détectée.")