# 🕵️ William Higgons Screener – Stock Selection App

This app was built to mimic the rigorous approach of William Higgons (fund manager at Indépendance & Expansion) for selecting undervalued yet financially robust European stocks.

It is intended to serve as a real-world portfolio simulator and personal stock screener for active value investing.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://william-higgons-stock-screener.streamlit.app/)
Link of the website : https://william-higgons-stock-screener.streamlit.app/

## ❓ Why this project?

As a value investing and data enthusiast, I wanted to build a production-ready app that combines:

- 🔍 **Financial filtering engine** using `pandas` to screen ~1,500 Euronext stocks (PEA eligible) from custom-cleaned `yfinance` data
- 🧠 **Business logic encoding** of William Higgons’ investment criteria (PER < 12, ROE > 10%, revenue growth > 0%), applied row-wise via scoring functions
- 📊 **Interactive dashboards** built with `Streamlit` and `Plotly`, including emoji-enriched tables, sparklines, and yfinance-powered stock charts
- ⚙️ **Automated data pipeline** using GitHub Actions to refresh financial data daily and trigger automatic app redeployments (CI/CD)

## 📈 Investment Criteria (William Higgons)

A stock is considered **eligible** if it meets *all* of the following:

- ✅ PER (Price Earnings Ratio) < 12
- ✅ ROE (Return on Equity) > 10%
- ✅ Revenue growth > 0% (YoY)

**Exit rules:**
- PER > 15 → partial exit (20% per PER point)
- PER > 20 → full exit
- 6-month stop loss if unrealized loss

---

## 🧠 Higgons Score (/100)

Each stock receives a score based on:
- PER (lower = better)
- ROE (higher = better)
- Revenue growth rate
- Defensive sector bonus (Healthcare / Consumer Defensive)

---

## 🚀 Features

- 🔎 Interactive filtering by country, sector, PER, ROE, growth
- 📋 Emoji-enriched stock table with Higgons score
- 📈 Auto-generated price charts using `yfinance`
- 🧾 Custom written business diagnostics
- 🧪 Backtesting module vs European indices (WIP)
- 🔁 GitHub Actions auto-refresh (daily update)

---

## 🧰 Tech Stack

- Python 3.10+
- Streamlit
- pandas / numpy
- yfinance
- plotly
- GitHub Actions (CI/CD)

---

## ✍️ Author
Built by [Théo Naïm Bouyahia](https://www.linkedin.com/in/th%C3%A9o-na%C3%AFm-benhellal-56bb6218a/)  

---

## 📂 Folder Structure

```shell
├── app.py               # Main Streamlit app
├── data/                # Cleaned CSVs (PEA eligible stocks)
├── utils/               # Scoring & diagnostic logic
├── .github/workflows/   # GitHub Actions auto-update
├── requirements.txt
└── README.md

## ✍️ Author
Built by [Théo Naïm Bouyahia](https://www.linkedin.com/in/th%C3%A9o-na%C3%AFm-benhellal-56bb6218a/)  
