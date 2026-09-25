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
capacity = st.sidebar.slider("Energy Capacity (MWh)", 0.5, 10.0, 2.0, 0.5)
max_power = st.sidebar.slider("Max Power (MW)", 0.25, 5.0, 1.0, 0.25)
efficiency = st.sidebar.slider("Round-Trip Efficiency (%)", 80.0, 98.0, 92.0, 1.0) / 100.0

# Market prices profile
hours = list(range(24))
default_prices = [
    65, 55, 45, 40, 42, 50, 70, 90,    
    80, 50, 30, 15, 10, 12, 20, 45,    
    75, 110, 130, 120, 95, 80, 70, 60 
]

# Run optimization model
timesteps = range(len(default_prices))
model = pulp.LpProblem("Streamlit_BESS_Opt", pulp.LpMaximize)

# Safe definition for PuLP variables without keyword clashes
p_charge = {t: pulp.LpVariable(f"Charge_{t}", lowBound=0, upBound=max_power, cat='Continuous') for t in timesteps}
p_discharge = {t: pulp.LpVariable(f"Discharge_{t}", lowBound=0, upBound=max_power, cat='Continuous') for t in timesteps}
soc = {t: pulp.LpVariable(f"SoC_{t}", lowBound=0, upBound=capacity, cat='Continuous') for t in range(len(default_prices) + 1)}
is_charging = {t: pulp.LpVariable(f"IsCharging_{t}", cat='Binary') for t in timesteps}

model += pulp.lpSum(
    default_prices[t] * (p_discharge[t] * np.sqrt(efficiency) - p_charge[t] / np.sqrt(efficiency)) 
    for t in timesteps
)

model += (soc[0] == capacity * 0.5)
M = max_power * 2
for t in timesteps:
    model += (soc[t+1] == soc[t] + p_charge[t] * np.sqrt(efficiency) - p_discharge[t] / np.sqrt(efficiency))
    model += (p_charge[t] <= M * is_charging[t])
    model += (p_discharge[t] <= M * (1 - is_charging[t]))

model += (soc[len(default_prices)] >= capacity * 0.5)
model.solve(pulp.PULP_CBC_CMD(msg=0))

results = []
for t in timesteps:
    results.append({
        "Hour": t,
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
ax.bar(df_res['Hour'], df_res['Discharge (MW)'], color='green', alpha=0.7, label='Discharge (Selling)')
ax.bar(df_res['Hour'], [-val for val in df_res['Charge (MW)']], color='red', alpha=0.7, label='Charge (Buying)')
ax.set_ylabel('Power Dispatch (MW)')
ax.set_xlabel('Hour of Day')
ax.legend()
st.pyplot(fig)
