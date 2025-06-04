import pandas as pd
import yfinance as yf
from tqdm import tqdm
from datetime import datetime

# === 📥 Chargement des tickers propres ===
df_clean = pd.read_csv("data/all_results_yfinance_clean.csv")
tickers = df_clean["Ticker"].dropna().unique().tolist()

# === 🔁 Boucle d'analyse ===
results = []

for ticker in tqdm(tickers, desc="🔁 Mise à jour des données"):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials
        balance_sheet = stock.balance_sheet

        price = info.get("currentPrice", None)
        eps = info.get("trailingEps", None)
        per = price / eps if price and eps and eps > 0 else None

        net_income = financials.loc["Net Income"].iloc[0] if "Net Income" in financials.index else None

        equity_candidates = [
            "Total Stockholder Equity",
            "Common Stock Equity",
            "Total Equity Gross Minority Interest"
        ]
        total_equity = next((balance_sheet.loc[k].iloc[0] for k in equity_candidates if k in balance_sheet.index), None)

        roe = (net_income / total_equity) * 100 if net_income and total_equity and total_equity != 0 else None

        revenue_2023 = financials.loc["Total Revenue"].iloc[0] if "Total Revenue" in financials.index else None
        revenue_2022 = financials.loc["Total Revenue"].iloc[1] if "Total Revenue" in financials.index and len(financials.loc["Total Revenue"]) > 1 else None
        revenue_growth = ((revenue_2023 - revenue_2022) / revenue_2022) * 100 if revenue_2023 and revenue_2022 and revenue_2022 != 0 else None

        sector = info.get("sector", None)
        industry = info.get("industry", None)

        results.append({
            "Ticker": ticker,
            "Price": price,
            "EPS": eps,
            "PER": round(per, 2) if per else None,
            "ROE (%)": round(roe, 2) if roe else None,
            "Revenue Growth (%)": round(revenue_growth, 2) if revenue_growth else None,
            "Sector": sector,
            "Industry": industry
        })

    except Exception as e:
        print(f"⚠️ Erreur sur {ticker} : {e}")

# === 💾 Sauvegarde des résultats ===
df_updated = pd.DataFrame(results)
df_updated = df_updated.dropna(subset=["Price", "EPS", "PER", "ROE (%)", "Revenue Growth (%)"])
df_updated.to_csv("data/all_results_yfinance_clean.csv", index=False)

# === 🕒 Écriture de la date de mise à jour ===
with open("data/last_update.txt", "w") as f:
    f.write(datetime.today().strftime("%Y-%m-%d"))

print("✅ Mise à jour terminée.")