# Grid-Nexus BESS Optimizer ⚡🔋

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://grid-nexus-bess-optimizer-b8by7r8hfzkdh2uvnv7skk.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced Mixed-Integer Linear Programming (MILP) optimization engine designed for Battery Energy Storage System (BESS) arbitrage in the German Day-Ahead electricity market. This tool simulates market price dynamics, optimizes charge/discharge schedules to maximize economic returns, and features an interactive web dashboard built with Streamlit.

🔗 **Live Application:** [Grid-Nexus BESS Optimizer on Streamlit](https://grid-nexus-bess-optimizer-b8by7r8hfzkdh2uvnv7skk.streamlit.app/)  
📂 **GitHub Repository:** [Mohammadrezarefaei/grid-nexus-bess-optimizer](https://github.com/Mohammadrezarefaei/grid-nexus-bess-optimizer)

---

## 🚀 Key Features

- **MILP Optimization Engine:** Powered by `PuLP`, formulated to optimize battery dispatch schedules against fluctuating hourly electricity prices.
- **Economic Arbitrage Modeling:** Maximizes revenue by buying energy during low-price or negative-price periods and discharging during peak-price hours, accounting for round-trip efficiency losses.
- **Interactive Web Dashboard:** Built with `Streamlit` and `Plotly`, allowing users to adjust battery parameters (capacity, max power, efficiency) in real-time and visualize financial performance.
- **Automated Reporting:** Generates clean dispatch schedules, market price charts, and performance logs stored in structured output directories.
- **Robust Testing Suite:** Comprehensive unit tests (`pytest`) ensuring mathematical correctness and solver reliability.

---

## 📂 Project Structure

```text
grid-nexus-bess-optimizer/
│
├── data/                  # Raw and sample market price datasets (e.g., ENTSO-E samples)
├── outputs/               # Generated optimization CSV reports and dispatch charts
├── src/                   # Core source code
│   └── optimization_engine.py  # MILP mathematical model & PuLP optimization logic
├── tests/                 # Unit tests for the optimization logic
│   └── test_optimizer.py  # Pytest suite
│
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
├── app.py                 # Streamlit web application entry point
├── grid-nexus-bess-optimizer.ipynb # Exploratory data analysis & prototyping notebook
└── requirements.txt       # Project dependencies
