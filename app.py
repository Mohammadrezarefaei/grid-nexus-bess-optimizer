import streamlit as st
import pandas as pd
import pulp
import plotly.graph_objects as go
import numpy as np

# تنظیمات اولیه صفحه
st.set_page_config(page_title="Grid-Nexus BESS Optimizer", layout="wide")
st.title("🔋 Battery Energy Storage System (BESS) Optimizer")

# --- 1. پارامترهای ورودی باتری ---
st.sidebar.header("BESS Parameters")
capacity_kwh = st.sidebar.number_input("Capacity (kWh)", value=100.0)
max_power_kw = st.sidebar.number_input("Max Power (kW)", value=50.0)
efficiency = st.sidebar.slider("Round-trip Efficiency", 0.8, 1.0, 0.9)
initial_soc = st.sidebar.slider("Initial SoC (%)", 0.0, 100.0, 50.0) / 100.0

eff_c = np.sqrt(efficiency)
eff_d = np.sqrt(efficiency)

# --- 2. آماده‌سازی داده‌ها ---
@st.cache_data
def load_data():
    # اصلاح فرکانس به 1h (حرف h کوچک برای نسخه‌های جدید پانداز)
    times = pd.date_range(start="2026-09-25", periods=24, freq="1h")
    prices = np.sin(np.linspace(0, 2 * np.pi, 24)) * 10 + 20 
    return pd.DataFrame({"Timestamp": times, "Price": prices})

df = load_data()
timesteps = df["Timestamp"].tolist()
prices = df["Price"].tolist()
N = len(df)

# --- 3. مدل‌سازی بهینه‌سازی ---
st.subheader("Optimization Results")

model = pulp.LpProblem("Streamlit_BESS_Opt", pulp.LpMaximize)

# تعریف متغیرها با ایندکس عددی برای جلوگیری از خطای فرمت تاریخ
p_charge = pulp.LpVariable.dicts("Charge", range(N), lowBound=0, upBound=max_power_kw, cat=pulp.LpContinuous)
p_discharge = pulp.LpVariable.dicts("Discharge", range(N), lowBound=0, upBound=max_power_kw, cat=pulp.LpContinuous)
soc = pulp.LpVariable.dicts("SoC", range(N), lowBound=0, upBound=capacity_kwh, cat=pulp.LpContinuous)

# تابع هدف
model += pulp.lpSum([prices[t] * (p_discharge[t] - p_charge[t]) for t in range(N)]), "Total_Profit"

# محدودیت‌ها
for t in range(N):
    if t == 0:
        model += soc[t] == (initial_soc * capacity_kwh) + (p_charge[t] * eff_c) - (p_discharge[t] / eff_d)
    else:
        model += soc[t] == soc[t-1] + (p_charge[t] * eff_c) - (p_discharge[t] / eff_d)

status = model.solve()

# --- 4. نمایش نتایج ---
if pulp.LpStatus[status] == "Optimal":
    st.success(f
