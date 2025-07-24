import matplotlib.pyplot as plt
import streamlit as st  # 👈 add this line!

def get_user_inputs():
    print("\n📥 Please enter the following values (press Enter to use default):")

    def get_input(prompt, default):
        user_input = input(f"{prompt} [default: {default}]: ")
        return float(user_input) if user_input.strip() else float(default)

    power_kW = get_input("Enter Air Compressor Power Rating (kW)", 15)
    hours_per_day = get_input("Enter Operating Hours Per Day", 8)
    pressure = get_input("Enter Operating Pressure (Bar)", 7)
    efficiency = get_input("Enter System Efficiency (e.g. 0.85)", 0.85)
    electricity_cost = get_input("Enter Electricity Cost (£ per kWh)", 0.15)
    co2_factor = get_input("Enter CO₂ Emission Factor (kg per kWh, e.g. 0.92)", 0.92)

    print("\nSelect Compressor Type:")
    print("1. Reciprocating\n2. Rotary Screw\n3. Centrifugal")
    type_input = input("Enter the number corresponding to the compressor type [default: 1]: ")
    type_choice = int(type_input) if type_input.strip() else 1

    return power_kW, hours_per_day, pressure, efficiency, electricity_cost, co2_factor, type_choice


def get_loss_factors(type_choice):
    if type_choice == 1:
        compressor_type = 'Reciprocating'
        loss_factors = [0.15, 0.10, 0.05, 0.05, 0.05]
    elif type_choice == 2:
        compressor_type = 'Rotary Screw'
        loss_factors = [0.10, 0.05, 0.03, 0.02, 0.02]
    elif type_choice == 3:
        compressor_type = 'Centrifugal'
        loss_factors = [0.08, 0.03, 0.02, 0.01, 0.01]
    else:
        compressor_type = 'Unknown'
        loss_factors = [0.10, 0.05, 0.03, 0.02, 0.02]

    return compressor_type, loss_factors


def calculate_energy(power_kW, hours_per_day, efficiency, electricity_cost, co2_factor):
    daily_energy = power_kW * hours_per_day / efficiency
    monthly_energy = daily_energy * 30
    monthly_cost = monthly_energy * electricity_cost
    annual_co2 = monthly_energy * 12 * co2_factor
    return daily_energy, monthly_energy, monthly_cost, annual_co2


def calculate_energy_loss(daily_energy, loss_factors):
    input_energy = daily_energy
    leak_loss = input_energy * loss_factors[0]
    idle_loss = input_energy * loss_factors[1]
    pressure_loss = input_energy * loss_factors[2]
    overcap_loss = input_energy * loss_factors[3]
    heat_loss = input_energy * loss_factors[4]

    useful_energy = input_energy - (leak_loss + idle_loss + pressure_loss + overcap_loss + heat_loss)

    return input_energy, leak_loss, idle_loss, pressure_loss, overcap_loss, heat_loss, useful_energy

def plot_energy_breakdown(leak_loss, idle_loss, pressure_loss, overcap_loss, heat_loss, useful_energy, labels):
    values = [leak_loss, idle_loss, pressure_loss, overcap_loss, heat_loss, useful_energy]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, values, color="#00f9ff", edgecolor="#39ff14")

    ax.set_facecolor("#0b0c10")
    fig.patch.set_facecolor("#0b0c10")
    ax.spines['bottom'].set_color('#00f9ff')
    ax.spines['left'].set_color('#00f9ff')
    ax.tick_params(colors='white')
    ax.set_title("Energy Use Breakdown", color="#00f9ff")
    ax.set_ylabel("Energy (kWh)", color="#c5c6c7")
    ax.set_xticklabels(labels, rotation=45)

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}", ha='center', color="#39ff14")

    st.pyplot(fig)
