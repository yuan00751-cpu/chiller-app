import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(
    page_title="Chiller Efficiency & COP Simulator Dashboard (SB)",
    page_icon="❄️",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 26px;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2563EB;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">❄️ Chiller Efficiency & COP Simulator Dashboard (SB)</div>', unsafe_allow_html=True)

# Sidebar Inputs
st.sidebar.header("⚙️ Inputs & Parameters")

flow = st.sidebar.number_input("Chilled Water Flow (m³/h)", value=115.5, step=1.0)
chwr = st.sidebar.number_input("CHWR Temp (°C)", value=12.0, step=0.1)
chws = st.sidebar.number_input("CHWS Temp (°C)", value=7.0, step=0.1)
power = st.sidebar.number_input("Chiller Power (kW)", value=125.0, step=1.0)

# Calculations
delta_t = chwr - chws
cooling_capacity_kw = flow * delta_t * 1.163
cooling_capacity_rt = cooling_capacity_kw / 3.517

cop = cooling_capacity_kw / power if power > 0 else 0
ikw_rt = power / cooling_capacity_rt if cooling_capacity_rt > 0 else 0

# Status Indicator
if ikw_rt < 0.65:
    status_color = "#16A34A"
    status_text = "EXCELLENT"
elif ikw_rt <= 0.80:
    status_color = "#CA8A04"
    status_text = "GOOD"
else:
    status_color = "#DC2626"
    status_text = "POOR"

# Display Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Cooling Load (RT)", value=f"{cooling_capacity_rt:.2f} RT")
with col2:
    st.metric(label="COP", value=f"{cop:.2f}")
with col3:
    st.metric(label="Efficiency (kW/RT)", value=f"{ikw_rt:.3f}")
with col4:
    st.markdown(f"""
        <div class="metric-card">
            <small>Status Rating</small><br>
            <strong style="color: {status_color}; font-size: 20px;">{status_text}</strong>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Charts
st.subheader("📊 Performance Analysis")

fig, ax1 = plt.subplots(figsize=(10, 4))

# Generate dummy simulation data based on current input
loads = np.linspace(cooling_capacity_rt * 0.3, cooling_capacity_rt * 1.1, 20)
cops = [cop * (1 - 0.0008 * (l - cooling_capacity_rt)**2) for l in loads]

ax1.set_xlabel('Cooling Load (RT)', fontsize=10)
ax1.set_ylabel('COP', color='#1E3A8A', fontsize=10)
line1 = ax1.plot(loads, cops, color='#2563EB', linewidth=2.5, label='COP Curve')
ax1.tick_params(axis='y', labelcolor='#1E3A8A')
ax1.grid(True, linestyle='--', alpha=0.5)

st.pyplot(fig)
