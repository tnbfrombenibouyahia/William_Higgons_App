import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np



# === Configuration de la page ===
st.set_page_config(page_title="William Higgons Screener", layout="wide")
st.title("📊 Screener William Higgons")


with st.expander("📖 Comprendre la stratégie William Higgons", expanded=False):
    st.video("https://www.youtube.com/watch?v=Ct3ZDvUjCFI")
    
    st.markdown("""
    **🔍 Objectif de l'app**  
    Cet outil permet d’identifier les entreprises européennes cotées qui répondent aux **critères stricts de sélection de William Higgons**, célèbre investisseur value.  
    L’objectif est de bâtir un portefeuille diversifié de **33 sociétés à 3% chacune**, avec un suivi rigoureux.

    **📋 Critères de sélection ("Screening")**
    Pour qu’une entreprise soit considérée comme **validée** :
    - 🔻 **PER < 12** → L’action n’est pas surévaluée (ratio Prix / Bénéfice faible).
    - 💸 **ROE > 10%** → L’entreprise est rentable (Rentabilité des Fonds Propres).
    - 📈 **Chiffre d’affaires en croissance** → Le CA doit être supérieur à l’année précédente.

    **⚖️ Règle de sortie du portefeuille**
    - ❌ Si le **PER dépasse 20**, on **vend toute la position**.
    - 📉 À partir de **15 de PER**, on vend **20% de la position par point de PER**.
    - 🔴 Si une **position est en perte depuis 6 mois**, elle est coupée.

    **📊 Score Higgons (/100)**
    Pour affiner la sélection, un score est calculé selon :
    - Le niveau de PER (plus bas = mieux),
    - Le ROE (plus élevé = mieux),
    - La croissance du chiffre d'affaires,
    - La nature défensive du secteur.

    ---
    👉 Utilise les filtres ci-dessous pour explorer les sociétés. Celles qui passent les critères apparaissent en **vert**.
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

df["Score_Higgons_Numerique"] = df.apply(compute_higgons_score, axis=1)

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


df_filtered["🎯 Score Higgons"] = df_filtered.apply(compute_higgons_score, axis=1)
df_filtered["🎯 Score Higgons Texte"] = df_filtered["🎯 Score Higgons"].apply(
    lambda x: "— Rejeté" if pd.isna(x) else f"{int(x)}/100"
)

# Renommage des colonnes
df_display = df_filtered.drop(columns=["Higgons Valid"]).rename(columns={
    "Ticker": "🔖 Ticker",
    "Pays": "🌍 Pays",
    "Sector": "🏷️ Secteur",
    "Industry": "🏭 Industrie",
    "🧠 Statut": "✅ Filtre William Higgons",
    "🎯 Score Higgons Texte": "🎯 Score Higgons (sur 100)",
    "Price": "💰 Cours de l'action (€)",
    "EPS": "📊 Bénéfice par action (EPS)",
    "PER": "📉 Price Earning Ratio (PER)",
    "ROE (%)": "🏦 Rentabilité des fonds propres (%)",
    "Revenue Growth (%)": "📈 Croissance du chiffre d'affaires (%)"
})

# Réorganisation des colonnes
column_order = [
    "🔖 Ticker", "🌍 Pays", "🏷️ Secteur", "🏭 Industrie",
    "✅ Filtre William Higgons", "🎯 Score Higgons (sur 100)",
    "💰 Cours de l'action (€)", "📊 Bénéfice par action (EPS)",
    "📉 Price Earning Ratio (PER)", "🏦 Rentabilité des fonds propres (%)",
    "📈 Croissance du chiffre d'affaires (%)"
]

df_display = df_display[column_order]

st.dataframe(df_display, use_container_width=True)

# === Diagnostic automatique détaillé ===
def genere_bilan_qualitatif(row):
    per = row["PER"]
    roe = row["ROE (%)"]
    growth = row["Revenue Growth (%)"]
    sector = row.get("Sector", "")
    ticker = row["Ticker"]

    per_score = 3 if per < 8 else 2 if per < 10 else 1 if per < 15 else 0
    roe_score = 3 if roe > 20 else 2 if roe > 15 else 1 if roe > 10 else 0
    growth_score = 3 if growth > 10 else 2 if growth > 5 else 1 if growth > 0 else 0

    total_score = per_score + roe_score + growth_score
    defensif = any(x in str(sector) for x in ["Healthcare", "Consumer Defensive"])

    if total_score >= 8:
        scenario = "🟢 Excellent"
        texte = (
            f"✅ L'entreprise **{ticker}** affiche un **PER de {per:.1f}**, indiquant qu'elle est **très faiblement valorisée par rapport à ses bénéfices**.\n"
            f"✅ Son **ROE atteint {roe:.1f}%**, ce qui traduit une **très forte rentabilité** des capitaux investis.\n"
            f"✅ Elle enregistre une **croissance du chiffre d'affaires de {growth:.1f}%**, preuve d'une **expansion soutenue**.\n"
            f"👉 {ticker} présente ainsi une **excellente opportunité d’investissement** selon les standards Higgons."
        )
    elif total_score >= 6:
        scenario = "🟢 Très bon"
        texte = (
            f"👍 **{ticker}** affiche un **PER de {per:.1f}**, une rentabilité (**ROE**) de {roe:.1f}% et une croissance de {growth:.1f}%.\n"
            f"Elle coche la majorité des critères fondamentaux. Cette entreprise présente une **base financière solide**\n"
            f"et une **valorisation raisonnable**, ce qui en fait un bon candidat pour un portefeuille long terme."
        )
    elif total_score >= 4:
        scenario = "🟠 Moyen"
        texte = (
            f"⚠️ Le profil financier de **{ticker}** est mitigé : **PER de {per:.1f}**, **ROE de {roe:.1f}%**, et une croissance de {growth:.1f}%.\n"
            f"Bien qu'elle reste stable, **l’absence de catalyseur fort** pourrait limiter sa performance.\n"
            f"{ticker} peut convenir à une stratégie de diversification, **sans être une conviction forte**."
        )
    else:
        scenario = "🔴 À fuir"
        texte = (
            f"❌ L’analyse de **{ticker}** montre un **PER de {per:.1f}** élevé ou peu pertinent, un **ROE faible ({roe:.1f}%)**,\n"
            f"et une **croissance quasi inexistante ({growth:.1f}%)**.\n"
            f"🔻 Selon les critères de William Higgons, **{ticker} ne présente pas un profil d’investissement attractif**."
        )

    if defensif:
        texte += f"\n\n🛡️ À noter : **{ticker}** appartient à un **secteur défensif**, ce qui peut offrir une meilleure résilience en période de marché incertain."

    return f"### 🧾 Diagnostic automatique : {scenario}\n\n{texte}"

# Ce bloc doit être appelé après l'affichage du graphique dans l'analyse individuelle

# === Analyse individuelle ===
st.markdown("---")
st.subheader("📊 Analyse individuelle")

if not df_display.empty:
    selected_ticker = st.text_input(
        "🔍 Entrer un ticker pour afficher son graphique :",
        value = df_display["🔖 Ticker"].iloc[0] if not df_display.empty else ""
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

            
            # juste après st.plotly_chart(...)
            ligne = df_filtered[df_filtered["Ticker"] == selected_ticker]
            if not ligne.empty:
                bilan = genere_bilan_qualitatif(ligne.iloc[0])
                st.markdown(bilan)


# === Date de mise à jour ===
st.markdown("---")
try:
    with open("data/last_update.txt", "r") as f:
        last_update = f.read().strip()
    st.info(f"🕒 Dernière mise à jour automatique des données : `{last_update}`")
except FileNotFoundError:
    st.warning("⚠️ Aucune mise à jour automatique détectée.")

## -------- TESTING TESTING ---------

# === Backtest dynamique de la stratégie William Higgons ===
st.markdown("---")
st.subheader("📆 Backtest dynamique de la stratégie William Higgons")

col_start, col_end, col_index = st.columns(3)
with col_start:
    start_date = st.date_input("📅 Date de début", pd.to_datetime("2020-01-01"))
with col_end:
    end_date = st.date_input("📅 Date de fin", pd.to_datetime("2025-01-01"))
with col_index:
    benchmark_symbol = st.selectbox("📊 Indice de comparaison", ["^STOXX50E", "^FCHI", "^GSPC", "^IXIC", "^GDAXI"])

if st.button("🚀 Lancer le backtest"):
    try:
        # Vérifie et ajoute la colonne Score Higgons si elle n'existe pas dans df
        if "🎯 Score Higgons" not in df.columns:
            df["🎯 Score Higgons"] = df.apply(compute_higgons_score, axis=1)

        # Sélection des 33 meilleures entreprises validées selon Score Higgons
        top_33_tickers = df[df["Higgons Valid"] == True] \
                            .sort_values("🎯 Score Higgons", ascending=False) \
                            .head(33)["Ticker"].tolist()

        st.info(f"📥 Téléchargement des données pour les 33 tickers sélectionnés + {benchmark_symbol}...")
        prices = yf.download(top_33_tickers + [benchmark_symbol], start=start_date, end=end_date)

        # Vérifie qu'Adj Close est bien disponible, sinon fallback sur 'Close'
        if "Adj Close" in prices.columns:
            prices = prices["Adj Close"]
        elif "Close" in prices.columns:
            prices = prices["Close"]
        else:
            raise ValueError("Aucune colonne 'Adj Close' ou 'Close' trouvée dans les données téléchargées.")

        # Nettoyage des colonnes avec données manquantes
        prices = prices.dropna(axis=1)

        # Séparation portefeuille / benchmark
        portfolio_prices = prices.drop(columns=[benchmark_symbol])
        benchmark_prices = prices[benchmark_symbol]

        # Pondération égale
        weights = np.full(len(portfolio_prices.columns), 1 / len(portfolio_prices.columns))
        portfolio_perf = (portfolio_prices / portfolio_prices.iloc[0]) @ weights
        benchmark_perf = benchmark_prices / benchmark_prices.iloc[0]

        # Graphique comparatif
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=portfolio_perf.index, y=portfolio_perf,
                                 name="Portefeuille William Higgons (Top 33)", line=dict(width=3)))
        fig.add_trace(go.Scatter(x=benchmark_perf.index, y=benchmark_perf,
                                 name=f"Indice ({benchmark_symbol})", line=dict(width=2, dash='dash')))
        fig.update_layout(
            title="📈 Performance du portefeuille vs indice de référence",
            xaxis_title="Date",
            yaxis_title="Performance (base 100)",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Résumé chiffré
        port_return = round((portfolio_perf[-1] - 1) * 100, 2)
        bench_return = round((benchmark_perf[-1] - 1) * 100, 2)

        col1, col2 = st.columns(2)
        col1.metric("📈 Performance du portefeuille", f"{port_return}%")
        col2.metric("📉 Performance de l'indice", f"{bench_return}%")

    except Exception as e:
        st.error(f"⚠️ Erreur durant le backtest : {e}")