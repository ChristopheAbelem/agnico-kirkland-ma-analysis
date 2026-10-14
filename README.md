# M&A Post-Mortem: Agnico Eagle & Kirkland Lake Gold

**Live dashboard: [agnico-kirkland-merger.streamlit.app](https://agnico-kirkland-merger.streamlit.app)**

A post-mortem of the 2021–2022 all-stock merger of equals between Agnico Eagle Mines (AEM) and
Kirkland Lake Gold (KL), valued at C$13.5B (about US$10.7B at announcement). The project
reconstructs the deal terms and tests whether the promised synergies ($800M over 5 years, pre-tax)
explain the combined company's results, using peers (Newmont and Barrick) as a benchmark.

## Question

Did the merger work? More precisely: is there evidence in margins, unit costs, stock returns and
valuation that the merger created value beyond what the gold price and the sector delivered?

## Verdict

Partially. AEM kept unit-cost growth below its peers' and its stock moved from lagging them before
the announcement to leading them after. But the reported synergies explain only a small part of the
cost advantage, margin expansion follows the gold price, and other events (notably the 2023
acquisition of Yamana's Canadian assets) occurred in the same period. The data cannot isolate how
much of the outperformance is due to the merger.

## Tests and results

| Test | What it checks | Result |
|---|---|---|
| Announcement reaction | Market's first read of the deal | AEM −1.6% on day 0 vs peers +1%; outperformed by 3.6 pts at +5 days and 5.7 at +20 |
| Stock returns before vs after | Whether outperformance predates the deal | Before: AEM +31% vs +70% / +44%. After: +320% vs +147% / +162% |
| Margins vs peers | Whether margin gains are merger-specific | Operating margin +28 pts at AEM vs +35 (NEM) and +20 (B): shared across the sector |
| Gold price check | Whether margins follow the gold price | 2022–2025: gold +92%, AEM revenue +107%, cost of revenue +33% |
| Unit costs (AISC) | Cost performance independent of gold | AEM +23% vs +33% (NEM) and +34% (B): about $150–165/oz less cost growth |
| Pre-merger cost baseline | First-year synergy effect | AISC +14% in 2022, same as Newmont: no visible first-year drop |
| Reported synergies | Delivery vs promise | About $150M through 2023 (incl. ~$90M guidance) vs $800M 5-year target; explain at most a fifth to a quarter of the cost gap |
| Detour Lake (asset level) | Largest inherited mine vs plan | Costs +34% vs +23% company-wide, 46% above the July 2022 plan; synergy too small to detect |
| Valuation (P/E) | Whether the market pays a premium | 2024–2025: AEM 19–21x vs 13–16x for peers |

## Repository structure

```
agnico-kirkland-ma-analysis/
├── dashboard/
│   ├── app.py                            # Streamlit dashboard
│   └── data/                             # CSV tables exported by the notebook
├── notebooks/
│   └── agnico_kirkland_analysis.ipynb    # Full analysis, methodology and sources
├── data/                                 # SQLite database (created by the notebook, not tracked)
├── requirements.txt
└── README.md
```

The notebook holds the full analysis: data collection, method notes, every calculation and the
sources. The dashboard summarizes the results visually and reads only the exported CSV files.

## Setup

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the notebook to rebuild the database and the dashboard data, then start the dashboard:

```bash
streamlit run dashboard/app.py
```

## Data sources

- Prices and financial statements: yfinance (AEM, NEM, B, COMEX gold futures)
- Deal terms, synergies, AISC, total cash costs and the Detour Lake plan: AEM, Kirkland Lake,
  Newmont and Barrick filings and results releases (SEC 6-K / 40-F, company websites)

## Limitations

- No counterfactual: there is no way to observe AEM without the merger.
- Confounding events: the 2023 Yamana acquisition; Newmont's Newcrest acquisition in 2023.
- yfinance provides only 2022–2025 financials, so there are no pre-merger margins; Kirkland Lake
  (delisted) is not available.
- No company synergy totals after 2023; the 2023 amounts are guidance, and the five-year window
  has not yet ended.
- AISC definitions differ across companies; the 2021 pro forma baseline is an estimate.
- Gold is a futures proxy, not AEM's realized price; P/E uses reported diluted EPS.

## Tools

Python, pandas, SQLAlchemy, SQLite, matplotlib, Streamlit, Plotly.