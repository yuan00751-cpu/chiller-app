import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="Chiller Efficiency & COP Simulator Dashboard | SB",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #3B82F6;
        margin-bottom: 0px;
    }
    .brand-badge {
        background-color: #1E3A8A;
        color: #93C5FD;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 15px;
    }
    .kpi-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    .kpi-title {
        color: #9CA3AF;
        font-size: 0.95rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        color: #F9FAFB;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 8px 0;
    }
    .kpi-subtext {
        color: #6B7280;
        font-size: 0.85rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize History State
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar Controls
st.sidebar.markdown("## ⚙️ Control Inputs")
st.sidebar.markdown("---")

flow = st.sidebar.number_input("Chilled Water Flow (m³/h)", value=175.5, step=1.0, format="%.1f")
chwr = st.sidebar.number_input("CHWR Temp (°C)", value=6.3, step=0.1, format="%.1f")
chws = st.sidebar.number_input("CHWS Temp (°C)", value=3.0, step=0.1, format="%.1f")
power = st.sidebar.number_input("Total Chiller Power (kW)", value=179.0, step=1.0, format="%.1f")

st.sidebar.markdown("---")
record_name = st.sidebar.text_input("📝 Note / Tag for Record", value="Normal Operation")

# Primary Calculations
delta_t = chwr - chws
cooling_kw = (flow * 1000 * 4.186 * delta_t) / 3600
cooling_ton = cooling_kw / 3.517
cop = cooling_kw / power if power > 0 else 0
kw_per_ton = power / cooling_ton if cooling_ton > 0 else 0

if st.sidebar.button("💾 Save Record to History"):
    new_entry = {
        "Tag": record_name,
        "Flow (m³/h)": flow,
        "CHWR (°C)": chwr,
        "CHWS (°C)": chws,
        "ΔT (°C)": round(delta_t, 2),
        "Power (kW)": power,
        "Capacity (TON)": round(cooling_ton, 2),
        "COP": round(cop, 2),
        "kW/TON": round(kw_per_ton, 2)
    }
    st.session_state.history.insert(0, new_entry)
    st.sidebar.success("Record saved successfully!")

# Main Dashboard Header
col_header, col_brand = st.columns([4, 1])
with col_header:
    st.markdown('<div class="main-header">❄️ Chiller Performance Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-badge">DEVELOPED BY : SB</div>', unsafe_allow_html=True)

# Top Key Metrics Cards
k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Cooling Capacity</div>
        <div class="kpi-value" style="color:#60A5FA;">{cooling_ton:.1f} <span style="font-size:1.2rem;">TON</span></div>
        <div class="kpi-subtext">Calculated Thermal Load ({cooling_kw:.1f} kW)</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Chiller COP</div>
        <div class="kpi-value" style="color:#34D399;">{cop:.2f}</div>
        <div class="kpi-subtext">Coefficient of Performance</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Specific Power</div>
        <div class="kpi-value" style="color:#FBBF24;">{kw_per_ton:.2f} <span style="font-size:1.2rem;">kW/TON</span></div>
        <div class="kpi-subtext">Efficiency Metric</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs Navigation
tab1, tab2 = st.tabs(["🎛️ What-If Simulation & Trend", "📜 History Logs"])

with tab1:
    st.subheader("🎛️ What-If Simulation (CHWS Temperature Setpoint)")
    sim_chws = st.slider("Simulate CHWS Temperature Target (°C)", min_value=1.0, max_value=10.0, value=float(chws), step=0.5)

    temp_diff = sim_chws - chws
    sim_power = power * (1 - (temp_diff * 0.025))
    sim_delta_t = chwr - sim_chws
    sim_cooling_kw = (flow * 1000 * 4.186 * sim_delta_t) / 3600
    sim_cop = sim_cooling_kw / sim_power if sim_power > 0 else 0
    sim_kw_ton = sim_power / (sim_cooling_kw / 3.517) if sim_cooling_kw > 0 else 0
    energy_saving = temp_diff * 2.5

    s_col1, s_col2, s_col3 = st.columns(3)
    s_col1.metric("Simulated COP", f"{sim_cop:.2f}", f"{(sim_cop - cop):+.2f}")
    s_col2.metric("Simulated Specific Power", f"{sim_kw_ton:.2f} kW/TON", f"{(sim_kw_ton - kw_per_ton):+.2f} kW/TON", delta_color="inverse")
    s_col3.metric("Est. Energy Saving", f"{energy_saving:+.1f} %")

    # Interactive Plotly Trend
    temps = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    cops = []
    kw_tons = []

    for t in temps:
        d_pwr = power * (1 - ((t - chws) * 0.025))
        d_dt = chwr - t
        d_kw = (flow * 1000 * 4.186 * d_dt) / 3600
        d_ton = d_kw / 3.517
        cops.append(d_kw / d_pwr if d_pwr > 0 else 0)
        kw_tons.append(d_pwr / d_ton if d_ton > 0 else 0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=temps, y=cops, mode='lines+markers', name='COP', line=dict(color='#34D399', width=3)))
    fig.add_trace(go.Scatter(x=temps, y=kw_tons, mode='lines+markers', name='kW/TON', line=dict(color='#FBBF24', width=3, dash='dot')))
    fig.add_vline(x=chws, line_dash="dash", line_color="#EF4444", annotation_text=f"Current Setpoint ({chws}°C)")

    fig.update_layout(
        title="CHWS Temperature Setpoint vs Performance Trend",
        xaxis_title="CHWS Temp (°C)",
        yaxis_title="Metric Value",
        template="plotly_dark",
        height=380,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📜 Saved Calculation History")
    if len(st.session_state.history) > 0:
        df_history = pd.DataFrame(st.session_state.history)
        st.dataframe(df_history, use_container_width=True)

        col_dl, col_clr = st.columns([3, 1])
        with col_dl:
            csv_data = df_history.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download History (CSV)", csv_data, "chiller_history_SB.csv", "text/csv")
        with col_clr:
            if st.button("🗑️ Clear History"):
                st.session_state.history = []
                st.rerun()
    else:
        st.info("ยังไม่มีประวัติที่บันทึกไว้ (สามารถกดปุ่ม '💾 Save Record to History' ที่แถบด้านซ้ายเพื่อบันทึกประวัติการคำนวณได้)")
