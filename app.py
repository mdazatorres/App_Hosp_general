import streamlit as st
import pandas as pd
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go
import plotly.express as px
from aux_functions import create_flow_diagram, solve_equilibrium, simulate_dynamics

# Page configuration
st.set_page_config(layout="wide", page_title="Hospital Compartment Model Builder")
st.title("🏥 Hospital Compartment Model Builder")

# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = {}
if 'current_params' not in st.session_state:
    st.session_state.current_params = {}


# =====================================================
# SELECT UNITS
# =====================================================
def get_selected_units():
    st.sidebar.header("Select hospital units")

    use_ed = st.sidebar.checkbox("Emergency Department", True)
    use_ward = st.sidebar.checkbox("General Ward (Med-Surg / Auxiliary)")
    use_icu = st.sidebar.checkbox("ICU")
    use_step = st.sidebar.checkbox("Step-down / PCU")

    units = []
    if use_ed:   units.append("ED")
    if use_ward: units.append("WARD")
    if use_icu:  units.append("ICU")
    if use_step: units.append("STEP")

    return units


# =====================================================
# BASE DATA
# =====================================================
BASE_DATA = {
    "ED": ["daily_ED_arrivals", "left_without_being_seen", "avg_ED_wait_time", "avg_ED_boarding_time",
           "avg_ED_length_of_stay", "total_adm_from_ED"],
    "WARD": ["ward_occupied_beds", "ward_discharges", "ward_direct_admission", "ward_transfer_admission", "ward_to_ICU"],
    "STEP": ["stepdown_occupied_beds", "stepdown_discharges", "stepdown_direct_admission", "stepdown_transfer_admission",
             "stepdown_to_ICU", "stepdown_to_ward"],
    "ICU": ["ICU_occupied_beds", "ICU_discharges", "ICU_direct_admission", "ICU_transfer_admission", 'ICU_to_stepdown','ICU_to_ward']
}


# =====================================================
# PARAMETERS
# =====================================================
BASE_PARAMS = {"ED": ["sigma", "omega", "gamma", "pED_to_step", "pED_to_ward", "pED_to_ICU", "xi_step", "xi_ward", "xi_ICU"],
    "WARD": ["ward_discharge_rate", "ward_to_ICU_rate"],
    "STEP": ["step_discharge_rate", "step_to_ICU_rate", "step_to_ward_rate"],
    "ICU": ["ICU_discharge_rate", "ICU_to_ward_rate", "ICU_to_step_rate"]}

selected_units = get_selected_units()
required_data = set()
required_params = set()

for u in selected_units:
    required_data.update(BASE_DATA.get(u, []))
    required_params.update(BASE_PARAMS.get(u, []))


# =====================================================
# CONDITIONAL TRANSFERS
# =====================================================
def add_transfer(a, b, name):
    if a in selected_units and b in selected_units:
        required_data.add(name)


add_transfer("ED", "WARD", "ED_to_ward_admissions")
add_transfer("ED", "STEP", "ED_to_stepdown_admissions")
add_transfer("ED", "ICU", "ED_to_ICU_admissions")

# =====================================================
# FLOW STRUCTURE
# =====================================================
flows = []


def add_flow(a, b):
    if a in selected_units and b in selected_units:
        flows.append((a, b))


add_flow("ED", "WARD")
add_flow("ED", "STEP")
add_flow("ED", "ICU")
add_flow("WARD", "ICU")
add_flow("ICU", "WARD")
add_flow("WARD", "STEP")
add_flow("STEP", "WARD")
add_flow("ICU", "STEP")
add_flow("STEP", "ICU")


# =====================================================
# BUILD ODE SYSTEM
# =====================================================
def build_equations(units):
    eqs = []

    # ---------------- ED ----------------
    if "ED" in units:
        eqs.append(r"\frac{dW}{dt} = \lambda - (\sigma + \omega)W")
        eqs.append(r"\frac{dS}{dt} = \sigma W - \gamma S")

        if "WARD" in units:
            eqs.append(r"\frac{dB_{ward}}{dt} = p_{ED\to ward}\gamma S - \xi_{ward}B_{ward}")

        if "STEP" in units:
            eqs.append(r"\frac{dB_{step}}{dt} = p_{ED\to step}\gamma S - \xi_{step}B_{step}")

        if "ICU" in units:
            eqs.append(r"\frac{dB_{ICU}}{dt} = p_{ED\to ICU}\gamma S - \xi_{ICU}B_{ICU}")

    # ---------------- WARD ----------------
    if "WARD" in units:
        inflow = [r"A^{dir}_{ward}", r"T_{ward}"]

        if "ED" in units:
            inflow.append(r"\xi_{ward}B_{ward}")

        if "ICU" in units:
            inflow.append(r"\rho_{ICU\to ward}ICU")

        if "STEP" in units:
            inflow.append(r"\rho_{step\to ward}STEP")

        outflow = [r"\mu_{ward}WARD"]

        if "ICU" in units:
            outflow.append(r"\rho_{ward\to ICU}WARD")

        # if "STEP" in units:
        #     outflow.append(r"\rho_{ward\to step}WARD")

        eqs.append(r"\frac{dWARD}{dt} = " + " + ".join(inflow)
                   + " - (" + " + ".join(outflow) + ")")

    # ---------------- STEP ----------------
    if "STEP" in units:
        inflow = [r"A^{dir}_{step}", r"T_{step}"]

        if "ED" in units:
            inflow.append(r"\xi_{step}B_{step}")

        if "ICU" in units:
            inflow.append(r"\rho_{ICU\to step}ICU")

        # if "WARD" in units:
        #     inflow.append(r"\rho_{ward\to step}WARD")

        outflow = [r"\mu_{step}STEP"]

        if "ICU" in units:
            outflow.append(r"\rho_{step\to ICU}STEP")

        if "WARD" in units:
            outflow.append(r"\rho_{step\to ward}STEP")

        eqs.append(r"\frac{dSTEP}{dt} = " + " + ".join(inflow)
                   + " - (" + " + ".join(outflow) + ")")

    # ---------------- ICU ----------------
    if "ICU" in units:
        inflow = [r"A^{dir}_{ICU}", r"T_{ICU}"]

        if "ED" in units:
            inflow.append(r"\xi_{ICU}B_{ICU}")

        if "WARD" in units:
            inflow.append(r"\rho_{ward\to ICU}WARD")

        if "STEP" in units:
            inflow.append(r"\rho_{step\to ICU}STEP")

        outflow = [r"\mu_{ICU}ICU"]

        if "WARD" in units:
            outflow.append(r"\rho_{ICU\to ward}ICU")

        if "STEP" in units:
            outflow.append(r"\rho_{ICU\to step}ICU")

        eqs.append(r"\frac{dICU}{dt} = " + " + ".join(inflow)
                   + " - (" + " + ".join(outflow) + ")")

    return eqs


# =====================================================
# CREATE FLOW DIAGRAM
# =====================================================



# =====================================================
# GET OPERATIONAL INPUTS
# =====================================================
# def get_operational_inputs(required_data):
#     st.sidebar.header("Hospital operational data")
#
#     mode = st.sidebar.radio(
#         "Provide values:",["Manual entry", "Upload Excel"])
#
#     values = {}
#
#     # ===============================
#     # EXCEL UPLOAD
#     # ===============================
#     if mode == "Upload Excel":
#         file = st.sidebar.file_uploader("Upload Excel", type=["xlsx", "xls"])
#
#         if file:
#             try:
#                 df = pd.read_excel(file)
#
#                 # Check if dataframe has required columns
#                 if 'variable' in df.columns and 'value' in df.columns:
#                     for _, row in df.iterrows():
#                         values[row["variable"]] = float(row["value"])
#                     st.sidebar.success(f"✅ Loaded {len(values)} values")
#                 else:
#                     st.sidebar.error("Excel must have 'variable' and 'value' columns")
#             except Exception as e:
#                 st.sidebar.error(f"Error loading file: {e}")
#
#     # ===============================
#     # MANUAL ENTRY
#     # ===============================
#     else:
#         st.sidebar.markdown("### Enter planning values")
#
#         # Create columns for better organization
#         col1, col2 = st.sidebar.columns(2)
#
#         for i, v in enumerate(sorted(required_data)):
#             if i % 2 == 0:
#                 with col1:
#                     values[v] = st.number_input(v.replace('_', ' ').title(),
#                                                 min_value=0.0, value=0.0, step=1.0, format="%.2f")
#             else:
#                 with col2:
#                     values[v] = st.number_input(v.replace('_', ' ').title(),
#                                                 min_value=0.0, value=0.0, step=1.0, format="%.2f")
#
#     return values


# =====================================================
# GET OPERATIONAL INPUTS
# =====================================================
def get_operational_inputs(required_data):
    st.sidebar.header("Hospital operational data")

    mode = st.sidebar.radio(
        "Provide values:", ["Manual entry", "Upload Excel"])

    values = {}

    # Define default values dictionary
    DEFAULT_VALUES = {
        # ED defaults
        'daily_ED_arrivals': 270.82,
        'left_without_being_seen': 7.15,
        'avg_ED_wait_time': 0.078,
        'avg_ED_boarding_time': 0.676,
        'avg_ED_length_of_stay': 0.316,
        'total_adm_from_ED': 50.02,
        'ED_to_ward_admissions': 35.04,
        'ED_to_stepdown_admissions': 1.44,
        'ED_to_ICU_admissions': 6.58,
#
        # Ward defaults
        'ward_occupied_beds': 400.33,
        'ward_discharges': 66.37,
        'ward_direct_admission': 9.27,
        'ward_transfer_admission': 7.63,
        'ward_to_ICU':  2.98,

        # Step-down defaults
        'stepdown_occupied_beds': 8.39,
        'stepdown_discharges': 2.33,
        'stepdown_direct_admission': 5.28,
        'stepdown_transfer_admission': 0.59,
        'stepdown_to_ICU': 0.78,
        'stepdown_to_ward': 3.52, # check this

        # ICU defaults
        'ICU_occupied_beds': 76.94,
        'ICU_discharges': 3.05,
        'ICU_direct_admission': 2.09,
        'ICU_transfer_admission': 3.37,
        'ICU_to_stepdown': 0.1,
        'ICU_to_ward': 12.80,
    }

    # ===============================
    # EXCEL UPLOAD
    # ===============================
    if mode == "Upload Excel":
        file = st.sidebar.file_uploader("Upload Excel", type=["xlsx", "xls"])

        if file:
            try:
                df = pd.read_excel(file)

                # Check if dataframe has required columns
                if 'variable' in df.columns and 'value' in df.columns:
                    for _, row in df.iterrows():
                        values[row["variable"]] = float(row["value"])
                    st.sidebar.success(f"✅ Loaded {len(values)} values")
                else:
                    st.sidebar.error("Excel must have 'variable' and 'value' columns")
            except Exception as e:
                st.sidebar.error(f"Error loading file: {e}")

    # ===============================
    # MANUAL ENTRY WITH DEFAULTS
    # ===============================
    else:
        st.sidebar.markdown("### Enter planning values")

        # Create columns for better organization
        col1, col2 = st.sidebar.columns(2)

        for i, v in enumerate(sorted(required_data)):
            # Get default value from dictionary, or 0.0 if not found
            default_val = DEFAULT_VALUES.get(v, 0.0)

            if i % 2 == 0:
                with col1:
                    values[v] = st.number_input(
                        v.replace('_', ' ').title(),
                        min_value=0.0,
                        value=default_val,
                        step=1.0,
                        format="%.2f",
                        key=f"input_{v}"  # Add unique key to avoid duplicate ID issues
                    )
            else:
                with col2:
                    values[v] = st.number_input(
                        v.replace('_', ' ').title(),
                        min_value=0.0,
                        value=default_val,
                        step=1.0,
                        format="%.2f",
                        key=f"input_{v}"
                    )

    return values


# =====================================================
# COMPUTE PARAMETERS FROM DATA
# =====================================================
def compute_parameters_from_entry(values):
    """
    Compute model parameters from input data
    """
    params = {}

    # Check if we have the required data
    if not values:
        return get_default_parameters(selected_units)

    # ===== ED PARAMETERS =====
    if "ED" in selected_units:
        # Get ED values with defaults
        mean_LOS = float(values.get('avg_ED_length_of_stay', 1))
        mean_wait = float(values.get('avg_ED_wait_time', 0.5))
        mean_board = float(values.get('avg_ED_boarding_time', 0.5))
        total_arr = float(values.get('daily_ED_arrivals', 100))
        total_lwbs = float(values.get('left_without_being_seen', 5))
        total_adm_from_ED=float(values.get('total_adm_from_ED', 5))

        # Wait time to treatment rate
        params["sigma"] = 1.0 / max(mean_wait, 1e-6)

        # Left without being seen calculation
        if total_arr > 0:
            f_lwbs = min(total_lwbs / total_arr, 0.99)  # Cap at 0.99
            params["omega"] = params["sigma"] * f_lwbs / max((1.0 - f_lwbs), 1e-9)
        else:
            params["omega"] = 0.1

        # Admission probabilities
        seen_total = max(total_arr - total_lwbs, 1e-6)

        if seen_total <= 0:
            p_admit = 0.15  # fallback
        else:
            p_admit = total_adm_from_ED / seen_total

        # Get admission counts with defaults
        ed_to_ward = float(values.get('ED_to_ward_admissions', total_arr * 0.3))
        ed_to_step = float(values.get('ED_to_stepdown_admissions', total_arr * 0.1))
        ed_to_icu = float(values.get('ED_to_ICU_admissions', total_arr * 0.05))

        params["pED_to_ward"] = min(ed_to_ward / seen_total, 1.0)
        params["pED_to_step"] = min(ed_to_step / seen_total, 1.0)
        params["pED_to_ICU"] = min(ed_to_icu / seen_total, 1.0)

        # Treatment rate (service time)
        mean_service = max(mean_LOS - mean_wait - p_admit*mean_board,1e-6)
        params["gamma"] = 1.0 / mean_service

        # Boarding rates
        params["xi_ward"] = 1.0 / max(mean_board, 1e-6)
        params["xi_step"] = 1.0 / max(mean_board, 1e-6)
        params["xi_ICU"] = 1.0 / max(mean_board, 1e-6)

    # ===== WARD PARAMETERS =====
    if "WARD" in selected_units:
        ward_beds = float(values.get('ward_occupied_beds', 50))
        ward_beds = max(ward_beds, 1)
        # varphi
        params["ward_discharge_rate"] = float(values.get('ward_discharges', 20)) / ward_beds
        params["ward_to_ICU_rate"] = float(values.get('ward_to_ICU', 2)) / ward_beds
        params["ward_direct_admission_avg"]= values.get("ward_direct_admission")
        params["ward_transfer_admission_avg"] = values.get("ward_transfer_admission")


    # ===== STEP-DOWN PARAMETERS =====
    if "STEP" in selected_units:
        #psi
        step_beds = float(values.get('stepdown_occupied_beds', 10))
        step_beds = max(step_beds, 1)
        # varphi
        params["step_discharge_rate"] = float(values.get('stepdown_discharges', 12)) / step_beds
        params["step_to_ICU_rate"] = float(values.get("stepdown_to_ICU", 1)) / step_beds
        params["step_to_ward_rate"] = float(values.get("stepdown_to_ward", 1)) / step_beds
        params["stepdown_direct_admission_avg"] = values.get("stepdown_direct_admission")
        params["stepdown_transfer_admission_avg"] = values.get("stepdown_transfer_admission")



    # ===== ICU PARAMETERS =====
    if "ICU" in selected_units:
        icu_beds = float(values.get('ICU_occupied_beds', 20))
        icu_beds = max(icu_beds, 1)

        params["ICU_discharge_rate"] = float(values.get('ICU_discharges', 6)) / icu_beds
        params["ICU_to_ward_rate"] = float(values.get('ICU_to_ward', 3)) / icu_beds
        params["ICU_to_step_rate"] = float(values.get('ICU_to_stepdown', 3)) / icu_beds
        params["ICU_direct_admission_avg"] = values.get("ICU_direct_admission")
        params["ICU_transfer_admission_avg"] = values.get("ICU_transfer_admission")

        #params["ICU_to_ward_rate"] = float(values.get('ICU_transf', 3)) / icu_beds
        #params["ICU_to_step_rate"] = params["ICU_to_ward_rate"] * 0.3  # Estimate

    return params


def get_default_parameters(units):
    """Return default parameters based on selected units"""
    defaults = {}

    if "ED" in units:
        defaults.update({
            "sigma": 2.0,  # 0.5 day wait
            "omega": 0.2,
            "gamma": 1.0,  # 1 day treatment
            "pED_to_ward": 0.3,
            "pED_to_step": 0.1,
            "pED_to_ICU": 0.05,
            "xi_ward": 1.0,
            "xi_step": 1.0,
            "xi_ICU": 1.0
        })

    if "WARD" in units:
        defaults.update({
            "ward_discharge_rate": 0.5,
            "ward_to_ICU_rate": 0.05})

    if "STEP" in units:
        defaults.update({
            "step_discharge_rate": 0.4,
            "step_to_ICU_rate": 0.04,
            "step_to_ward_rate": 0.1})

    if "ICU" in units:
        defaults.update({
            "ICU_discharge_rate": 0.3,
            "ICU_to_ward_rate": 0.2,
            "ICU_to_step_rate": 0.05})

    return defaults






# =====================================================
# MAIN APP LAYOUT
# =====================================================

# Get operational inputs
values = get_operational_inputs(required_data)

# Compute parameters
params = compute_parameters_from_entry(values)
st.session_state.current_params = params

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Model Summary", "📊 Parameter Values",
    "⚖️ Equilibrium", "📈 Dynamics", "📑 Scenario Analysis"])

with tab1:
    st.header("Model Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Selected Units")
        for unit in selected_units:
            st.write(f"✅ {unit}")

    with col2:
        st.subheader("Hospital Flow Structure")
        if flows:
            flow_text = " → ".join([f"**{a}**" for a, b in flows[:3]])
            st.write("Patient flow pathways:")
            for a, b in flows:
                st.write(f"  • {a} → {b}")
        else:
            st.write("No flows defined")

    st.divider()

    st.subheader("Required Data Inputs")
    if required_data:
        # Display in columns
        data_list = sorted(required_data)
        cols = st.columns(3)
        for i, data in enumerate(data_list):
            cols[i % 3].write(f"• {data}")
    else:
        st.write("No data inputs required")

    st.divider()

    st.subheader("ODE System")
    equations = build_equations(selected_units)
    for eq in equations:
        st.latex(eq)

    st.divider()

    # Add flow diagram
    if len(selected_units) > 0:
        create_flow_diagram(selected_units, flows)

with tab2:
    st.header("Parameter Values")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Computed Parameters")
        if params:
            params_df = pd.DataFrame([
                {"Parameter": k, "Value": f"{v:.4f}", "Raw Value": v}
                for k, v in sorted(params.items())
            ])
            st.dataframe(params_df, use_container_width=True,
                         column_config={
                             "Raw Value": st.column_config.NumberColumn(format="%.4f")
                         })
        else:
            st.info("No parameters computed yet")

    with col2:
        st.subheader("Input Values")
        if values:
            input_df = pd.DataFrame([
                {"Variable": k, "Value": v}
                for k, v in sorted(values.items())
            ])
            st.dataframe(input_df, use_container_width=True,
                         column_config={
                             "Value": st.column_config.NumberColumn(format="%.2f")
                         })
        else:
            st.info("No input values provided")

with tab3:
    st.header("Equilibrium Analysis")

    if st.button("🔄 Calculate Equilibrium", type="primary"):
        if params and values:
            equilibrium = solve_equilibrium(selected_units, params, values)
        else:
            st.warning("Please provide input values first")

with tab4:
    st.header("Time Dynamics Simulation")

   # col1, col2 = st.columns([3, 1])


    simulation_days = st.number_input("Simulation days",
                                      min_value=1, max_value=365, value=30)

    if st.button("▶️ Run Simulation", type="primary"):
        if params and values and len(selected_units) > 0:
            simulate_dynamics(selected_units, params, values, days=simulation_days)
        else:
            st.warning("Please provide input values first")

    #with col1:
    st.info("""
        This simulation shows how patient numbers evolve over time based on the 
        compartment model. The system should reach equilibrium after sufficient time.

        **Initial conditions:**
        - Waiting area: 50 patients
        - Treatment area: 20 patients
        - Ward boarding: 30 patients
        - Step-down boarding: 15 patients
        - ICU boarding: 10 patients
        """)

# with tab5:
#     scenario_analysis()

# =====================================================
# SIDEBAR ADDITIONAL INFORMATION
# =====================================================
with st.sidebar:
    st.divider()
    st.markdown("### 📌 Model Information")
    st.markdown("""
    **Parameters:**
    - σ (sigma): Wait time to treatment rate
    - ω (omega): Left without being seen rate
    - γ (gamma): Treatment completion rate
    - ξ (xi): Boarding area transfer rate
    - μ (mu): Unit discharge rate
    - ρ (rho): Inter-unit transfer rate

    **Units:**
    - ED: Emergency Department
    - WARD: General Ward
    - STEP: Step-down/PCU
    - ICU: Intensive Care Unit
    """)

    # Show current configuration
    st.divider()
    st.markdown(f"**Current configuration:** {', '.join(selected_units) if selected_units else 'None'}")
    st.markdown(f"**Number of parameters:** {len(params)}")
    st.markdown(f"**Number of input values:** {len(values)}")

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.caption("Hospital Compartment Model Builder v2.0 | Built with Streamlit")


# To do
# 1) check that the parameters are computed with the default values, because I am defining some initial values
# for the model's parameters like omege, sigma
# 2) make the parameter computing available for an excel file
# 3) create an Excel file as an example to be upload
# 4) if there is data plot along the equilibrium
# 4) Add scenarios option, one time the equilibrium is computed, we can make scenarios as we did for UC Davis