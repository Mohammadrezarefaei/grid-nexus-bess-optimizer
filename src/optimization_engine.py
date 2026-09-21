import pulp
import pandas as pd
import numpy as np

def optimize_bess_arbitrage(prices, capacity_mwh=2.0, max_power_mw=1.0, efficiency=0.92):
    """
    Solves a MILP optimization problem for BESS Day-Ahead arbitrage.
    """
    timesteps = range(len(prices))
    model = pulp.LpProblem("Grid_Nexus_BESS_Arbitrage", pulp.LpMaximize)
    
    # Decision Variables
    p_charge = pulp.LpVariable.dicts("Charge", timesteps, lowBound=0, upBound=max_power_mw)
    p_discharge = pulp.LpVariable.dicts("Discharge", timesteps, lowBound=0, upBound=max_power_mw)
    soc = pulp.LpVariable.dicts("SoC", range(len(prices) + 1), lowBound=0, upBound=capacity_mwh)
    is_charging = pulp.LpVariable.dicts("IsCharging", timesteps, cat='Binary')
    
    # Objective Function: Maximize profit
    model += pulp.lpSum(
        prices[t] * (p_discharge[t] * np.sqrt(efficiency) - p_charge[t] / np.sqrt(efficiency)) 
        for t in timesteps
    )
    
    # Constraints
    model += (soc[0] == capacity_mwh * 0.5)
    M = max_power_mw * 2
    
    for t in timesteps:
        model += (soc[t+1] == soc[t] + p_charge[t] * np.sqrt(efficiency) - p_discharge[t] / np.sqrt(efficiency))
        model += (p_charge[t] <= M * is_charging[t])
        model += (p_discharge[t] <= M * (1 - is_charging[t]))
        
    model += (soc[len(prices)] >= capacity_mwh * 0.5)
    
    # Solve model
    model.solve(pulp.PULP_CBC_CMD(msg=0))
    
    # Extract results
    results = []
    for t in timesteps:
        results.append({
            "Hour": t,
            "Price (€/MWh)": prices[t],
            "Charge (MW)": p_charge[t].varValue,
            "Discharge (MW)": p_discharge[t].varValue,
            "SoC (MWh)": soc[t+1].varValue
        })
        
    return pd.DataFrame(results), pulp.LpStatus[model.status]
