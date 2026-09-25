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

# تبدیل به نوع داده float استاندارد پایتون برای سازگاری کامل با PuLP 2.8.0
eff_c = float(np.sqrt(efficiency))
eff_d = float(np.sqrt(efficiency))

# محاسبه معکوس راندمان دشارژ برای جلوگیری از خطای تقسیم در PuLP
inv_eff_d = 1.0 / eff_d

# --- 2. آماده‌سازی داده‌ها ---
@st.cache_data
def load_data():
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

# تعریف متغیرها
p_charge = pulp.LpVariable.dicts("Charge", range(N), lowBound=0, upBound=max_power_kw, cat=pulp.LpContinuous)
p_discharge = pulp.LpVariable.dicts("Discharge", range(N), lowBound=0, upBound=max_power_kw, cat=pulp.LpContinuous)
soc = pulp.LpVariable.dicts("SoC", range(N), lowBound=0, upBound=capacity_kwh, cat=pulp.LpContinuous)

# تابع هدف
model += pulp.lpSum([prices[t] * (p_discharge[t] - p_charge[t]) for t in range(N)]), "Total_Profit"

# محدودیت‌ها (استفاده از ضرب معکوس به جای تقسیم)
for t in range(N):
    if t == 0:
        model += soc[t] == (initial_soc * capacity_kwh) + (p_charge[t] * eff_c) - (p_discharge[t] * inv_eff_d)
    else:
        model += soc[t] == soc[t-1] + (p_charge[t] * eff_c) - (p_discharge[t] * inv_eff_d)

status = model.solve()

# --- 4. نمایش نتایج ---
if pulp.LpStatus[status] == "Optimal":
    st.success(f"Optimization Successful! Total Profit: €{pulp.value(model.objective):.2f}")
    
    results = pd.DataFrame({
        "Timestamp": timesteps,
        "Price (€/MWh)": prices,
        "Charge (kW)": [p_charge[t].varValue for t in range(N)],
        "Discharge (kW)": [p_discharge[t].varValue for t in range(N)],
        "SoC (kWh)": [soc[t].varValue for t in range(N)]
    })
    
    results["Net Power (kW)"] = results["Discharge (kW)"] - results["Charge (kW)"]

    # رسم نمودارها
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=results["Timestamp"], y=results["Price (€/MWh)"], 
                             mode='lines', name='Price', yaxis="y1", line=dict(color='gray', dash='dot')))
    
    fig.add_trace(go.Bar(x=results["Timestamp"], y=results["Net Power (kW)"], 
                         name='BESS Power (Net)', yaxis="y2", marker_color='blue'))
    
    fig.add_trace(go.Scatter(x=results["Timestamp"], y=results["SoC (kWh)"] / capacity_kwh * 100, 
                             mode='lines', name='SoC (%)', yaxis="y3", line=dict(color='green', width=3)))

    fig.update_layout(
        title="BESS Operation Strategy",
        xaxis=dict(title="Time"),
        yaxis=dict(title="Price (€)", side="left", showgrid=False),
        yaxis2=dict(title="Power (kW)", side="right", overlaying="y", showgrid=False),
        yaxis3=dict(title="SoC (%)", side="right", overlaying="y", position=0.95, showgrid=False),
        legend=dict(x=0.01, y=0.99),
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(results)
    
else:
    st.error("Optimization failed to find an optimal solution. Check your constraints.")
