import streamlit as st
from functions import (
    get_loss_factors,
    calculate_energy,
    calculate_energy_loss,
    plot_energy_breakdown)

from datetime import datetime
import os

# ===== STYLING =====
st.markdown(
    """
    <style>
    body {
        background-image: url("https://images.unsplash.com/photo-1523966211575-eb4a01e7dd76?auto=format&fit=crop&w=1350&q=80");
        background-size: cover;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True)

st.markdown("""
<div style="font-family: monospace; font-size: 32px; color: #00f9ff; text-align:center;">
    <span style="animation: flicker 1.5s infinite alternate">⚙️ CAEEE SYSTEM v1.0 ⚙️</span>
</div>

<style>
@keyframes flicker {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# ===== SESSION STATE INIT =====
if "show_results" not in st.session_state:
    st.session_state.show_results = False

# ===== INPUT SCREEN =====
if not st.session_state.show_results:
    st.title("🚀 CAEEE – Compressed Air Energy Efficiency Estimator")
    st.markdown("Estimate energy use, cost, CO₂ emissions, and identify system inefficiencies.")

    st.markdown("## <span style='color:#00f9ff;'>🛠️ System Input Parameters</span>", unsafe_allow_html=True)
    power_kW = st.number_input("Compressor Power (kW)", min_value=1.0, value=15.0)
    hours_per_day = st.number_input("Operating Hours per Day", min_value=1.0, value=8.0)
    pressure = st.number_input("Operating Pressure (Bar)", min_value=1.0, value=7.0)
    efficiency = st.number_input("System Efficiency", min_value=0.1, max_value=1.0, value=0.85)
    electricity_cost = st.number_input("Electricity Cost (£/kWh)", min_value=0.01, value=0.15)
    co2_factor = st.number_input("CO₂ Emission Factor (kg/kWh)", min_value=0.01, value=0.92)

    compressor_type_choice = st.selectbox(
        "Compressor Type",
        ["Reciprocating", "Rotary Screw", "Centrifugal"]
    )

    if st.button("▶️ Run Estimator"):
        st.session_state.inputs = {
            "power_kW": power_kW,
            "hours_per_day": hours_per_day,
            "pressure": pressure,
            "efficiency": efficiency,
            "electricity_cost": electricity_cost,
            "co2_factor": co2_factor,
            "type_choice": compressor_type_choice
        }
        st.session_state.show_results = True
        st.rerun()

# ===== RESULTS SCREEN =====
else:
    st.markdown("## <span style='color:#00f9ff;'>📊 CAEEE Results Dashboard</span>", unsafe_allow_html=True)

    # Unpack values
    user_inputs = st.session_state.inputs
    power_kW = user_inputs["power_kW"]
    hours_per_day = user_inputs["hours_per_day"]
    pressure = user_inputs["pressure"]
    efficiency = user_inputs["efficiency"]
    electricity_cost = user_inputs["electricity_cost"]
    co2_factor = user_inputs["co2_factor"]
    compressor_type_choice = user_inputs["type_choice"]

    type_map = {"Reciprocating": 1, "Rotary Screw": 2, "Centrifugal": 3}
    type_choice = type_map[compressor_type_choice]

    # Calculations
    compressor_type, loss_factors = get_loss_factors(type_choice)
    daily_energy, monthly_energy, monthly_cost, annual_co2 = calculate_energy(
        power_kW, hours_per_day, efficiency, electricity_cost, co2_factor
    )
    input_energy, leak_loss, idle_loss, pressure_loss, overcap_loss, heat_loss, useful_energy = calculate_energy_loss(
        daily_energy, loss_factors
    )

    # ENERGY SUMMARY
    st.markdown("## <span style='color:#00f9ff;'>🔋 Energy Summary</span>", unsafe_allow_html=True)
    st.write(f"📅 Daily Energy Use   : **{daily_energy:.2f} kWh**")
    st.write(f"🗓️ Monthly Energy Use : **{monthly_energy:.2f} kWh**")
    st.write(f"💷 Monthly Cost       : **£{monthly_cost:.2f}**")
    st.write(f"🌍 Annual CO₂ Emission: **{annual_co2:.2f} kg**")

    # LOSS BREAKDOWN
    st.markdown("## <span style='color:#00f9ff;'>⚠️ Energy Loss Breakdown</span>", unsafe_allow_html=True)
    st.write(f"💨 Air Leaks         : {leak_loss:.2f} kWh")
    st.write(f"⏱️ Idle Running      : {idle_loss:.2f} kWh")
    st.write(f"📉 Pressure Drop     : {pressure_loss:.2f} kWh")
    st.write(f"⚖️ Overcapacity      : {overcap_loss:.2f} kWh")
    st.write(f"🔥 Heat Loss         : {heat_loss:.2f} kWh")
    st.write(f"✅ Useful Output     : {useful_energy:.2f} kWh")

    # PLOT
    labels = ["Air Leaks", "Idle Running", "Pressure Drop", "Overcapacity", "Heat Loss", "Useful Output"]
    plot_energy_breakdown(leak_loss, idle_loss, pressure_loss, overcap_loss, heat_loss, useful_energy, labels)

    # TIP
    st.markdown("## <span style='color:#00f9ff;'>💡 Suggested Action</span>", unsafe_allow_html=True)
    losses = [leak_loss, idle_loss, pressure_loss, overcap_loss, heat_loss]
    max_index = losses.index(max(losses))
    tips = [
        '🔧 Fix leaks using ultrasonic detectors',
        '🧠 Install automatic shutoff to reduce idle time',
        '📏 Check filters and piping layout to reduce pressure drop',
        '📉 Match compressor size to your actual demand',
        '🔥 Capture and reuse heat for other processes',
    ]
    st.success(f"📌 Suggested Action: **{tips[max_index]}**")

    # DOWNLOAD
    st.markdown("## <span style='color:#00f9ff;'>📁 Download Efficiency Report</span>", unsafe_allow_html=True)
    if st.button("📁 Download Report as TXT"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        filename = os.path.join(downloads_folder, f"CAEEE_Report_{timestamp}.txt")

        report_text = f"""
📘 Compressed Air Efficiency Report

Compressor Type: {compressor_type}
Daily Energy Use: {daily_energy:.2f} kWh
Monthly Energy Use: {monthly_energy:.2f} kWh
Monthly Cost: £{monthly_cost:.2f}
Annual CO₂ Emissions: {annual_co2:.2f} kg

--- Energy Loss Breakdown ---
Air Leaks: {leak_loss:.2f} kWh
Idle Running: {idle_loss:.2f} kWh
Pressure Drop: {pressure_loss:.2f} kWh
Overcapacity: {overcap_loss:.2f} kWh
Heat Loss: {heat_loss:.2f} kWh
Useful Output: {useful_energy:.2f} kWh

Main Efficiency Loss: {labels[max_index]}
Tip to Reduce Loss: {tips[max_index]}
"""
        with open(filename, "w", encoding="utf-8") as file:
            file.write(report_text.strip())
        st.success(f"✅ Report saved as `{filename}`")

    # BACK TO INPUT
    if st.button("🔄 Back to Input"):
        st.session_state.show_results = False
        st.rerun()
