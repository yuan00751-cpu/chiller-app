import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(
    page_title="Chiller Efficiency & COP Simulator Dashboard (SB)",
    page_icon="❄️",
    layout="wide"
)

# Dark Theme Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .main-header {
        font-size: 26px;
        font-weight: bold;
        color: #60A5FA;
        margin-bottom: 5px;
    }
    .brand-badge {
        background-color: #1E3A8A;
        color: #93C5FD;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #1a1f2c;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2d3748;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 2.0rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">❄️ Chiller Performance Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-badge">DEVELOPED BY : SB</div>', unsafe_allow_html=True)

# Sidebar Inputs
st.sidebar.title("⚙️ Control Inputs")
st.sidebar.markdown("---")

flow = st.sidebar.number_input("Chilled Water Flow (m³/h)", value=175.5, step=1.0)
chwr = st.sidebar.number_input("CHWR Temp (°C)", value=6.3, step=0.1)
chws = st.sidebar.number_input("CHWS Temp (°C)", value=3.0, step=0.1)
power = st.sidebar.number_input("Total Chiller Power (kW)", value=179.0, step=1.0)

# Calculations
delta_t = chwr - chws
cooling_kw = (flow * 1000 * 4.186 * delta_t) / 3600
cooling_ton = cooling_kw / 3.517
cop = cooling_kw / power if power > 0 else 0
kw_per_ton = power / cooling_ton if cooling_ton > 0 else 0

# Status Rating
if kw_per_ton > 0:
    if kw_per_ton <= 0.70:
        status_text, status_color = "EXCELLENT", "#34D399"
    elif kw_per_ton <= 0.85:
        status_text, status_color = "GOOD", "#FBBF24"
    else:
        status_text, status_color = "POOR", "#EF4444"
else:
    status_text, status_color = "N/A", "#9CA3AF"

# Display Metrics Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">COOLING CAPACITY</div>
        <div class="metric-value" style="color: #60A5FA;">{cooling_ton:.1f} <span style="font-size: 1.1rem;">TON</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">CHILLER COP</div>
        <div class="metric-value" style="color: #34D399;">{cop:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">SPECIFIC POWER</div>
        <div class="metric-value" style="color: #FBBF24;">{kw_per_ton:.2f} <span style="font-size: 1.1rem;">kW/TON</span></div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 5px solid {status_color};">
        <div class="metric-label">STATUS RATING</div>
        <div class="metric-value" style="color: {status_color};">{status_text}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown("---")

# What-If Simulation
st.subheader("🎛️ What-If Simulation (CHWS Temperature Setpoint)")
sim_chws = st.slider("Simulate CHWS Temperature Target (°C)", min_value=1.0, max_value=10.0, value=float(chws), step=0.5)

temp_diff = sim_chws - chws
sim_power = power * (1 - (temp_diff * 0.025))
sim_delta_t = chwr - sim_chws
sim_cooling_kw = (flow * 1000 * 4.186 * sim_delta_t) / 3600
sim_cop = sim_cooling_kw / sim_power if sim_power > 0 else 0
sim_kw_ton = sim_power / (sim_cooling_kw / 3.517) if sim_cooling_kw > 0 else 0
energy_saving = temp_diff * 2.5

sc1, sc2, sc3 = st.columns(3)
sc1.metric("Simulated COP", f"{sim_cop:.2f}", f"{(sim_cop - cop):+.2f}")
sc2.metric("Simulated Specific Power", f"{sim_kw_ton:.2f} kW/TON", f"{(sim_kw_ton - kw_per_ton):+.2f} kW/TON", delta_color="inverse")
sc3.metric("Est. Energy Saving", f"{energy_saving:+.1f} %")

st.write("")
st.subheader("📊 Performance Trend Chart")

# Native Streamlit Chart (No Plotly needed)
temps = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
chart_cops = []
chart_kw_tons = []

for t in temps:
    d_pwr = power * (1 - ((t - chws) * 0.025))
    d_dt = chwr - t
    d_kw = (flow * 1000 * 4.186 * d_dt) / 3600
    d_ton = d_kw / 3.517
    chart_cops.append(d_kw / d_pwr if d_pwr > 0 else 0)
    chart_kw_tons.append(d_pwr / d_ton if d_ton > 0 else 0)

chart_df = pd.DataFrame({
    'CHWS Temp (°C)': temps,
    'COP': chart_cops,
    'kW/TON': chart_kw_tons
}).set_index('CHWS Temp (°C)')

st.line_chart(chart_df)
