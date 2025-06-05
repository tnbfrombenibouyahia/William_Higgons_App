import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# === Configuration de la page ===
st.set_page_config(page_title="William Higgons Screener", layout="wide")
st.title("📊 Screener William Higgons")

# === Intro avec explications et vidéo
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

# === Chargement des données
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

# === 🎯 Score Higgons
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

    defensives = ["Healthcare", "Consumer Defensive"]
    if any(d in str(row["Sector"]) for d in defensives):
        score += 10

    return score

def genere_bilan_qualitatif(row):
    per = row["PER"]
    roe = row["ROE (%)"]
    growth = row["Revenue Growth (%)"]
    sector = row.get("Sector", "")

    # Scores individuels
    per_score = 3 if per < 8 else 2 if per < 10 else 1 if per < 15 else 0
    roe_score = 3 if roe > 20 else 2 if roe > 15 else 1 if roe > 10 else 0
    growth_score = 3 if growth > 10 else 2 if growth > 5 else 1 if growth > 0 else 0

    total_score = per_score + roe_score + growth_score

    # Détection secteur défensif
    defensif = any(x in str(sector) for x in ["Healthcare", "Consumer Defensive"])

    # Classification
    if total_score >= 8:
        scenario = "Excellent"
        texte = (
            f"✅ Cette entreprise présente un **PER de {per:.1f}**, ce qui suggère une **forte décote**.\n"
            f"Son **ROE atteint {roe:.1f}%**, preuve d'une **rentabilité exceptionnelle**.\n"
            f"Le chiffre d'affaires progresse de **{growth:.1f}%**, signe d'une **forte dynamique**.\n"
        )
    elif total_score >= 6:
        scenario = "Très bon"
        texte = (
            f"👍 Avec un **PER de {per:.1f}**, une rentabilité (**ROE**) de {roe:.1f}% et "
            f"une croissance de **{growth:.1f}%**, cette entreprise coche de **nombreux critères positifs**.\n"
        )
    elif total_score >= 4:
        scenario = "Moyen"
        texte = (
            f"⚠️ Le **PER de {per:.1f}**, le **ROE de {roe:.1f}%** et la croissance de **{growth:.1f}%** sont "
            f"mitigés. Cette société **n'est pas mauvaise**, mais **pas remarquable** selon les critères Higgons.\n"
        )
    else:
        scenario = "À fuir"
        texte = (
            f"❌ Un **PER de {per:.1f}**, un **ROE faible ({roe:.1f}%)** et une croissance de **{growth:.1f}%** "
            f"ne répondent **à aucun des critères de qualité attendus**.\n"
        )

    if defensif:
        texte += "🛡️ L'appartenance à un **secteur défensif** renforce néanmoins sa stabilité."
    
    return f"### 🧾 Diagnostic : {scenario}\n\n{texte}"



df["🎯 Score Higgons"] = df.apply(compute_higgons_score, axis=1)
df["🎯 Score Higgons Texte"] = df["🎯 Score Higgons"].apply(lambda x: "— Rejeté" if pd.isna(x) else int(x))

# === Filtres
st.sidebar.header("🧰 Filtres")

search_ticker = st.sidebar.text_input("🔎 Rechercher un ticker", "")
pays_filter = st.sidebar.selectbox("🌍 Pays", [""] + sorted(df["Pays"].unique()))
per_min, per_max = st.sidebar.slider("💰 PER", 0.0, 100.0, (0.0, 100.0))
roe_min = st.sidebar.slider("📈 ROE (%) minimum", 0.0, 100.0, 0.0)
growth_min = st.sidebar.slider("📊 Croissance min. (%)", -50.0, 100.0, 0.0)
only_higgons = st.sidebar.checkbox("✅ Seulement les sociétés validées")

# === Application des filtres
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

# === Renommage colonnes + affichage dans un ordre logique
df_display = df_filtered.rename(columns={
    "Price": "💶 Cours (€)",
    "EPS": "📊 Bénéfice par action",
    "PER": "📉 PER (Cours / Bénéfices)",
    "ROE (%)": "🏦 Rendement des fonds propres (%)",
    "Revenue Growth (%)": "📈 Croissance du chiffre d'affaires (%)",
    "Sector": "🏷️ Secteur",
    "Industry": "🏭 Industrie",
    "Pays": "🌍 Pays",
    "🧠 Statut": "✅ Filtre William Higgons",
    "🎯 Score Higgons Texte": "🎯 Score William Higgons (/100)"
})

# Réorganisation des colonnes pour affichage clair
colonnes_ordre = [
    "Ticker", "🌍 Pays", "🏭 Industrie", "🏷️ Secteur",  # Identification
    "✅ Filtre William Higgons", "🎯 Score William Higgons (/100)",  # Évaluation
    "💶 Cours (€)", "📊 Bénéfice par action", "📉 PER (Cours / Bénéfices)",
    "🏦 Rendement des fonds propres (%)", "📈 Croissance du chiffre d'affaires (%)"
]

df_display = df_display[[col for col in colonnes_ordre if col in df_display.columns]]

# === Affichage principal
# Convertir les types en string pour éviter ArrowTypeError
df_display["🎯 Score William Higgons (/100)"] = df_display["🎯 Score William Higgons (/100)"].astype(str)
st.dataframe(df_display, use_container_width=True)

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

                # Analyse qualitative
            ligne = df[df["Ticker"] == selected_ticker]
            if not ligne.empty:
                bilan = genere_bilan_qualitatif(ligne.iloc[0])
                st.markdown(bilan)

# === Dernière mise à jour
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        last_update = f.read().strip()
    st.info(f"🕒 Dernière mise à jour automatique des données : `{last_update}`")
except FileNotFoundError:
    st.warning("⚠️ Aucune mise à jour automatique détectée.")