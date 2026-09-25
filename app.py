import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pulp

st.set_page_config(page_title="Grid-Nexus BESS Optimizer", page_icon="⚡", layout="wide")

st.title("⚡ Grid-Nexus: Multi-Market BESS Optimization Engine")
st.markdown("Advanced MILP optimization tool for Day-Ahead arbitrage and battery dispatch management.")

# Sidebar parameters
st.sidebar.header("⚙️ Battery Specifications")
# Ensure float type for bounds
capacity = float(st.sidebar.slider("Energy Capacity (MWh)", 0.5, 10.0, 2.0, 0.5))
max_power = float(st.sidebar.slider("Max Power (MW)", 0.25, 5.0, 1.0, 0.25))
efficiency = float(st.sidebar.slider("Round-Trip Efficiency (%)", 80.0, 98.0, 92.0, 1.0)) / 100.0

# Market prices profile and time index with fixed freq="h"
@st.cache_data
def load_data():
    times = pd.date_range(start="2026-09-25", periods=24, freq="h")
    prices = [
        65, 55, 45, 40, 42, 50, 70, 90,    
        80, 50, 30, 15, 10, 12, 20, 45,    
        75, 110, 130, 120, 95, 80, 70, 60 
    ]
    return pd.DataFrame({"Timestamp": times, "Price": prices})

df_market = load_data()
default_prices = df_market["Price"].tolist()

# Run optimization model
timesteps = list(range(len(default_prices)))
model = pulp.LpProblem("Streamlit_BESS_Opt", pulp.LpMaximize)

# 100% POSITIONAL ARGUMENTS: (Name, LowerBound, UpperBound, Category)
# This completely bypasses the TypeError caused by keyword arguments on Streamlit Cloud
p_charge = {t: pulp.LpVariable(f"Charge_{t}", 0, max_power, pulp.LpContinuous) for t in timesteps}
p_discharge = {t: pulp.LpVariable(f"Discharge_{t}", 0, max_power, pulp.LpContinuous) for t in timesteps}
soc = {t: pulp.LpVariable(f"SoC_{t}", 0, capacity, pulp.LpContinuous) for t in range(len(default_prices) + 1)}
is_charging = {t: pulp.LpVariable(f"IsCharging_{t}", 0, 1, pulp.LpBinary) for t in timesteps}

model += pulp.lpSum(
    default_prices[t] * (p_discharge[t] * np.sqrt(efficiency) - p_charge[t] / np.sqrt(efficiency)) 
    for t in timesteps
)

model += (soc[0] == capacity * 0.5)
M = max_power * 2

for t in timesteps:
    # Physical constraints
    model += (soc[t+1] == soc[t] + p_charge[t] * np.sqrt(efficiency) - p_discharge[t] / np.sqrt(efficiency))
    
    # Big-M constraints for simultaneous charge/discharge prevention
    model += (p_charge[t] <= M * is_charging[t])
    model += (p_discharge[t] <= M * (1 - is_charging[t]))

model += (soc[len(default_prices)] >= capacity * 0.5)

# Solve the model quietly
model.solve(pulp.PULP_CBC_CMD(msg=0))

results = []
for t in timesteps:
    results.append({
        "Hour": t,
        "Timestamp": df_market["Timestamp"].iloc[t].strftime("%H:%M"),
        "Price (€/MWh)": default_prices[t],
        "Charge (MW)": p_charge[t].varValue,
        "Discharge (MW)": p_discharge[t].varValue,
        "SoC (MWh)": soc[t+1].varValue
    })
df_res = pd.DataFrame(results)

# Dashboard Layout
st.subheader("📋 Optimization Results Summary")
st.dataframe(df_res, use_container_width=True)

st.subheader("📊 Optimal Dispatch vs Market Prices")
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(df_res['Timestamp'], df_res['Discharge (MW)'], color='green', alpha=0.7, label='Discharge (Selling)')
ax.bar(df_res['Timestamp'], -df_res['Charge (MW)'], color='red', alpha=0.7, label='Charge (Buying)')
ax.set_ylabel('Power Dispatch (MW)')
ax.set_xlabel('Time')
plt.xticks(rotation=45)
ax.legend()
st.pyplot(fig)
