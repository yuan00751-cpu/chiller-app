import streamlit as st
import pandas as pd
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="Chiller Efficiency & COP Simulator Dashboard (SB)",
    page_icon="❄️",
    layout="wide"
)

# Custom High-Contrast Dark Theme CSS
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff !important;
    }
    
    /* Global Text Styling */
    p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    .main-header {
        font-size: 26px;
        font-weight: bold;
        color: #60A5FA !important;
        margin-bottom: 5px;
    }
    
    .brand-badge {
        background-color: #1E3A8A;
        color: #93C5FD !important;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 20px;
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: #1a1f2c;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2d3748;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
    }
    .metric-label {
        color: #94a3b8 !important;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    /* Legend Box */
    .legend-box {
        background-color: #151923;
        border-radius: 10px;
        padding: 12px 20px;
        border: 1px solid #2d3748;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-around;
        align-items: center;
    }

    /* FIX GENERAL BUTTON STYLE */
    .stButton>button {
        background-color: #1E40AF !important;
        color: #ffffff !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        background-color: #2563EB !important;
        border-color: #60A5FA !important;
    }

    /* 🎨 CUSTOM COLOR FOR GRAPH/ELEMENT TOOLBAR (ปุ่มดูกราฟเต็มจอ) */
    div[data-testid="stElementToolbar"] {
        background-color: #1E3A8A !important; /* พื้นหลังปุ่ม: น้ำเงินเข้ม */
        border: 1px solid #60A5FA !important;  /* เส้นขอบ: ฟ้าสว่าง */
        border-radius: 8px !important;
        padding: 2px 4px !important;
    }

    /* ไอคอนกล้อง/ไอคอนขยายจอ */
    div[data-testid="stElementToolbar"] button {
        background-color: #3B82F6 !important; /* ปุ่มสีฟ้า */
        color: #ffffff !important;
        border-radius: 6px !important;
        margin: 0 2px !important;
    }

    /* เปลี่ยนสีเมื่อเอาเมาส์ชี้ (Hover) */
    div[data-testid="stElementToolbar"] button:hover {
        background-color: #F97316 !important; /* เปลี่ยนเป็นสีส้มสว่าง */
    }

    div[data-testid="stElementToolbar"] svg {
        fill: #ffffff !important; /* เปลี่ยนสีไอคอนด้านในเป็นสีขาว */
    }

    /* Sidebar Background & Inputs */
    [data-testid="stSidebar"] {
        background-color: #111827;
    }
    [data-testid="stSidebar"] input {
        background-color: #1f2937 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State for History
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=[
        "Timestamp", "Flow (m³/h)", "CHWR (°C)", "CHWS (°C)", "Power (kW)", 
        "Cooling (TON)", "COP", "kW/TON", "Status"
    ])

# Header
st.markdown('<div class="main-header">❄️ Chiller Performance Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-badge">DEVELOPED BY : SB</div>', unsafe_allow_html=True)

# Sidebar Inputs
st.sidebar.title("⚙️ Control Inputs")
st.sidebar.markdown("---")

flow = st.sidebar.number_input("Chilled Water Flow (m³/h)", value=159.50, step=1.0)
chwr = st.sidebar.number_input("CHWR Temp (°C)", value=5.00, step=0.1)
chws = st.sidebar.number_input("CHWS Temp (°C)", value=4.20, step=0.1)
power = st.sidebar.number_input("Total Chiller Power (kW)", value=230.00, step=1.0)

# Calculations
delta_t = chwr - chws
cooling_kw = (flow * 1000 * 4.186 * delta_t) / 3600
cooling_ton = cooling_kw / 3.517
cop = cooling_kw / power if power > 0 else 0
kw_per_ton = power / cooling_ton if cooling_ton > 0 else 0

# Dynamic Color Assignment
if kw_per_ton > 0:
    if kw_per_ton <= 0.70:
        status_text, status_color = "EXCELLENT", "#34D399" # เขียว
    elif kw_per_ton <= 0.85:
        status_text, status_color = "GOOD", "#FBBF24"    # เหลือง
    else:
        status_text, status_color = "POOR", "#EF4444"    # แดง
else:
    status_text, status_color = "N/A", "#9CA3AF"

# Display Threshold Legend Box
st.markdown("""
<div class="legend-box">
    <span style="font-weight: bold; color: #94a3b8 !important;">📊 Efficiency Criteria (Specific Power):</span>
    <span style="color: #34D399 !important; font-weight: bold;">EXCELLENT : ≤ 0.70 kW/TON</span>
    <span style="color: #FBBF24 !important; font-weight: bold;">GOOD : 0.71 - 0.85 kW/TON</span>
    <span style="color: #EF4444 !important; font-weight: bold;">POOR : > 0.85 kW/TON</span>
</div>
""", unsafe_allow_html=True)

# Display Metrics Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">COOLING CAPACITY</div>
        <div class="metric-value" style="color: #60A5FA;">{cooling_ton:.1f} <span style="font-size: 1.0rem;">TON</span></div>
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
    <div class="metric-card" style="border-bottom: 4px solid {status_color};">
        <div class="metric-label">SPECIFIC POWER</div>
        <div class="metric-value" style="color: {status_color};">{kw_per_ton:.2f} <span style="font-size: 1.0rem;">kW/TON</span></div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 5px solid {status_color};">
        <div class="metric-label">STATUS RATING</div>
        <div class="metric-value" style="color: {status_color}; font-size: 1.5rem;">{status_text}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Button to Log History
btn_col1, btn_col2 = st.columns([2, 3])
with btn_col1:
    if st.button("💾 บันทึกค่าปัจจุบันลงประวัติ"):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([{
            "Timestamp": now_str,
            "Flow (m³/h)": flow,
            "CHWR (°C)": chwr,
            "CHWS (°C)": chws,
            "Power (kW)": power,
            "Cooling (TON)": round(cooling_ton, 1),
            "COP": round(cop, 2),
            "kW/TON": round(kw_per_ton, 2),
            "Status": status_text
        }])
        st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
        st.sidebar.success("บันทึกข้อมูลเรียบร้อย!")

# Table Cell Styling
def style_status(val):
    if val == "EXCELLENT":
        return 'background-color: #064e3b; color: #34D399; font-weight: bold;'
    elif val == "GOOD":
        return 'background-color: #713f12; color: #FBBF24; font-weight: bold;'
    elif val == "POOR":
        return 'background-color: #7f1d1d; color: #EF4444; font-weight: bold;'
    return ''

def style_kw_ton(val):
    if isinstance(val, (int, float)):
        if val <= 0.70:
            return 'background-color: #064e3b; color: #34D399; font-weight: bold;'
        elif val <= 0.85:
            return 'background-color: #713f12; color: #FBBF24; font-weight: bold;'
        else:
            return 'background-color: #7f1d1d; color: #EF4444; font-weight: bold;'
    return ''

# Display History Table
if not st.session_state.history.empty:
    st.subheader("📜 ประวัติการคำนวณย้อนหลัง (History Log)")
    styled_df = st.session_state.history.style.map(style_status, subset=['Status']).map(style_kw_ton, subset=['kW/TON'])
    st.dataframe(styled_df, use_container_width=True)
    
    if st.button("🗑️ ล้างประวัติทั้งหมด"):
        st.session_state.history = pd.DataFrame(columns=[
            "Timestamp", "Flow (m³/h)", "CHWR (°C)", "CHWS (°C)", "Power (kW)", 
            "Cooling (TON)", "COP", "kW/TON", "Status"
        ])
        st.rerun()

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

temps = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0]
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
