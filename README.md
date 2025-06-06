# 🕵️ William Higgons Screener – Stock Selection App

This project is a Streamlit-based web app designed to screen undervalued European stocks using the value investing criteria of William Higgons.

## 📈 Investment Criteria

An equity is considered **eligible** if it meets all the following:
- Price Earnings Ratio (PER) < 12
- Return on Equity (ROE) > 10%
- Revenue growth > 0% over last fiscal year

⚠️ Exit rules:
- PER > 20 → exit full position
- PER > 15 → partial exits (20% per point)
- Stop loss if in loss after 6 months

---

## 🧠 Higgons Score (/100)

Each company gets a score based on:
- PER level (lower is better)
- ROE level (higher is better)
- Revenue growth
- Defensive sector bonus

---

## 🚀 Features

- Dynamic filtering by sector, country, growth, ROE, PER
- Interactive tables with emoji-enriched sectors and industries
- Automatic stock graphs (via yfinance)
- Fundamental diagnostics (custom written)
- Backtest module vs European index (WIP)
- Auto-refresh & update tracking

---

## 📊 Stack

- Python 3.10+
- Streamlit
- Pandas / NumPy
- yfinance
- Plotly
- GitHub Actions (for automated updates)

---

## 📂 Project Structure

├── app.py              # Main Streamlit app
├── data/               # Cleaned CSVs
├── utils/              # Scoring & diagnostic logic
├── .github/workflows   # Auto-refresh workflow
├── requirements.txt
└── README.md

## ✍️ Author

Built by [Théo Naïm Bouyahia](https://www.linkedin.com/in/th%C3%A9o-na%C3%AFm-benhellal-56bb6218a/)  
