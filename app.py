import streamlit as st
import pandas as pd
import pulp
import plotly.graph_objects as go
import numpy as np

# تنظیمات اولیه صفحه استریم‌لیت
st.set_page_config(page_title="BESS Optimizer", layout="wide")
st.title("🔋 Battery Energy Storage System (BESS) Optimizer")

# --- 1. پارامترهای ورودی باتری (از سایدبار) ---
st.sidebar.header("BESS Parameters")
capacity_kwh = st.sidebar.number_input("Capacity (kWh)", value=100.0)
max_power_kw = st.sidebar.number_input("Max Power (kW)", value=50.0)
efficiency = st.sidebar.slider("Round-trip Efficiency", 0.8, 1.0, 0.9)
initial_soc = st.sidebar.slider("Initial SoC (%)", 0.0, 100.0, 50.0) / 100.0

# راندمان شارژ و دشارژ (جذر راندمان کل)
eff_c = np.sqrt(efficiency)
eff_d = np.sqrt(efficiency)

# --- 2. آماده‌سازی داده‌ها (می‌تونی دیتای خودت رو اینجا لود کنی) ---
@st.cache_data
def load_data():
    # ساخت یک دیتای فرضی 24 ساعته برای قیمت برق (مثلاً تعرفه داینامیک)
    times = pd.date_range(start="2026-09-25", periods=24, freq="1H")
    prices = np.sin(np.linspace(0, 2 * np.pi, 24)) * 10 + 20  # قیمت‌های سینوسی
    return pd.DataFrame({"Timestamp": times, "Price": prices})

df = load_data()
timesteps = df["Timestamp"].tolist()
prices = df["Price"].tolist()
N = len(df)  # تعداد کل استپ‌ها

# --- 3. مدل‌سازی بهینه‌سازی با PuLP ---
st.subheader("Optimization Results")

# تعریف مدل (هدف: بیشینه‌سازی سود یا کمینه‌سازی هزینه)
model = pulp.LpProblem("BESS_Arbitrage", pulp.LpMaximize)

# تعریف متغیرها با استفاده از ایندکس عددی (برای جلوگیری از ارور تایم‌ستپ)
# این کار ارور لاین 31 شما رو به طور کامل حل می‌کنه
P_charge = pulp.LpVariable.dicts("Charge_kW", range(N), lowBound=0, upBound=max_power_kw, cat=pulp.LpContinuous)
P_discharge = pulp.LpVariable.dicts("Discharge_kW", range(N), lowBound=0, upBound=max_power_kw, cat=pulp.LpContinuous)
SoC = pulp.LpVariable.dicts("SoC_kWh", range(N), lowBound=0, upBound=capacity_kwh, cat=pulp.LpContinuous)

# تابع هدف: ماکزیمم کردن سود (درآمد از دشارژ - هزینه شارژ)
model += pulp.lpSum([prices[t] * (P_discharge[t] - P_charge[t]) for t in range(N)]), "Total_Profit"

# محدودیت‌ها (Constraints)
for t in range(N):
    # 1. معادله تعادل وضعیت شارژ (State of Charge Balance)
    if t == 0:
        model += SoC[t] == (initial_soc * capacity_kwh) + (P_charge[t] * eff_c) - (P_discharge[t] / eff_d)
    else:
        model += SoC[t] == SoC[t-1] + (P_charge[t] * eff_c) - (P_discharge[t] / eff_d)
    
    # (اختیاری) جلوگیری از شارژ و دشارژ همزمان با تعریف متغیر باینری انجام می‌شود 
    # اما در مسائل آربیتراژ اقتصادی معمولاً به دلیل قیمت‌گذاری، خود الگوریتم همزمان شارژ و دشارژ نمی‌کند.

# حل مدل
status = model.solve()

# --- 4. استخراج نتایج و نمایش ---
if pulp.LpStatus[status] == "Optimal":
    st.success(f"Optimization Successful! Total Profit: €{pulp.value(model.objective):.2f}")
    
    # ساخت دیتافریم نتایج
    results = pd.DataFrame({
        "Timestamp": timesteps,
        "Price (€/MWh)": prices,
        "Charge (kW)": [P_charge[t].varValue for t in range(N)],
        "Discharge (kW)": [P_discharge[t].varValue for t in range(N)],
        "SoC (kWh)": [SoC[t].varValue for t in range(N)]
    })
    
    # خالص توان خروجی باتری
    results["Net Power (kW)"] = results["Discharge (kW)"] - results["Charge (kW)"]

    # --- 5. رسم نمودار با Plotly ---
    fig = go.Figure()
    
    # محور قیمت
    fig.add_trace(go.Scatter(x=results["Timestamp"], y=results["Price (€/MWh)"], 
                             mode='lines', name='Price', yaxis="y1", line=dict(color='gray', dash='dot')))
    
    # محور توان باتری
    fig.add_trace(go.Bar(x=results["Timestamp"], y=results["Net Power (kW)"], 
                         name='BESS Power (Net)', yaxis="y2", marker_color='blue'))
    
    # محور SoC
    fig.add_trace(go.Scatter(x=results["Timestamp"], y=results["SoC (kWh)"] / capacity_kwh * 100, 
                             mode='lines', name='SoC (%)', yaxis="y3", line=dict(color='green', width=3)))

    # تنظیمات ظاهری چارت چند محوره
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
    
    # نمایش جدول داده‌ها
    st.write("Detailed Timestep Data:")
    st.dataframe(results)
    
else:
    st.error("Optimization failed to find an optimal solution. Check your constraints.")
