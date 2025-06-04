import streamlit as st
import pandas as pd

# === Configuration de la page ===
st.set_page_config(page_title="William Higgons Screener", layout="wide")
st.title("📊 Screener William Higgons")

# === Chargement des données ===
@st.cache_data
def load_data():
    df = pd.read_csv("data/all_results_yfinance_clean.csv")

    df["Higgons Valid"] = (
        (df["PER"] < 12) &
        (df["ROE (%)"] > 10) &
        (df["Revenue Growth (%)"] > 0)
    )

    # Ajout du statut visuel
    df["💡 Statut"] = df["Higgons Valid"].apply(lambda x: "✅ Validé" if x else "❌ Rejeté")

    return df

df = load_data()

# === Affichage des données ===
st.markdown("### 🧾 Aperçu du screening")
st.write("Les entreprises **en vert** passent le filtre William Higgons.")

# === Mise en couleur conditionnelle ===
def highlight_higgons(row):
    return [
        "background-color: #d1e7dd; font-weight: bold;" if row["Higgons Valid"] else ""
        for _ in row
    ]

# === Affichage du tableau avec mise en forme ===
st.dataframe(
    df.style.apply(highlight_higgons, axis=1),
    use_container_width=True
)