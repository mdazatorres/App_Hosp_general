import streamlit as st
from core.equation_builder import build_equations
from core.data_manager import get_flows, get_selected_units, get_required_data
from core.data_processor import process_input_data
from utils.session_manager import initialize_session, update_current_params
from ui.tabs import (render_model_summary_tab, render_parameters_tab, render_equilibrium_tab, render_dynamics_tab, render_sidebar_info)
from ui.help_content import (QUICK_START_GUIDE, MODEL_CONFIGURATIONS, EQUATIONS_BY_MODEL, VARIABLE_DEFINITIONS, TIPS)
import numpy as np
# Add this to your imports if not already there
from ui.visualizations import (
    plot_units_comparison,
    plot_utilization_metrics)

# Page configuration
st.set_page_config(layout="wide", page_title="Hospital Compartment Model Builder")
st.title("🏥 Hospital Compartment Model Builder")

# Initialize session state
initialize_session()

# =====================================================
# GET USER CONFIGURATION
# =====================================================
selected_units = get_selected_units()
required_data = get_required_data(selected_units)
flows = get_flows(selected_units)

# =====================================================
# PROCESS INPUT DATA
# =====================================================
values, params = process_input_data(required_data, selected_units) # here I compute the parameters from excel or manual entry
update_current_params(params)

# =====================================================
# CREATE TABS
# =====================================================
tab1, tab2, tab3,   tab4 = st.tabs([
    "📋 Model Summary","⚖️ Equilibrium", "📑 Scenario Analysis", "❓ Help"])

with tab1:
    render_model_summary_tab(selected_units, flows, required_data)

#with tab2:
#    render_parameters_tab(params, values)
# This just for test any mistake

with tab2:
    render_equilibrium_tab(selected_units, params, values)

# with tab4:
#     render_dynamics_tab(selected_units, params, values)

with tab3:
    st.header("Surge Analysis")
    st.markdown("""
    Analyze the system's response to multiple surge events in different units.
    Define surge windows and amplitudes to see how the system responds.
    """)

    if not params or not values or not selected_units:
        st.warning("Please provide input values first")
    else:
        from core.surge_analysis import transient_response_for_multi_surge, plot_surge_response

        # Check if we have inpatient units
        inpatient_units = [u for u in ['STEP', 'WARD', 'ICU'] if u in selected_units]
        if not inpatient_units:
            st.warning("Surge analysis requires at least one inpatient unit (WARD, STEP, or ICU)")
        else:
            # Surge definition section
            st.subheader("Define Surge Events")

            surge_specs = {}

            for unit in inpatient_units:
                with st.expander(f"{unit} Unit Surges", expanded=(unit == inpatient_units[0])):
                    st.markdown(f"Define surge events for **{unit}** unit")

                    n_surges = st.number_input(
                        f"Number of surge events for {unit}",
                        min_value=0, max_value=5, value=0,
                        key=f"n_surges_{unit}"
                    )

                    unit_surges = []
                    for j in range(int(n_surges)):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            t_on = st.number_input(
                                f"Start day", min_value=0.0, value=5.0 + j * 10,
                                key=f"t_on_{unit}_{j}"
                            )
                        with col2:
                            t_off = st.number_input(
                                f"End day", min_value=t_on + 1, value=t_on + 5,
                                key=f"t_off_{unit}_{j}"
                            )
                        with col3:
                            amp = st.number_input(
                                f"Amplitude", min_value=0.0, value=5.0,
                                key=f"amp_{unit}_{j}"
                            )
                        unit_surges.append((t_on, t_off, amp))

                    if unit_surges:
                        surge_specs[unit] = unit_surges

            # Simulation parameters
            st.subheader("Simulation Parameters")
            col1, col2 = st.columns(2)
            with col1:
                t_end = st.number_input(
                    "Simulation end time (days)",
                    min_value=10.0, max_value=365.0, value=50.0
                )
            with col2:
                dt = st.number_input(
                    "Time step (days)",
                    min_value=0.1, max_value=5.0, value=0.5
                )

            # Run button
            if st.button("🚀 Run Surge Analysis", type="primary"):
                if surge_specs:
                    times = np.arange(0, t_end + dt, dt)

                    with st.spinner("Computing surge response..."):
                        results = transient_response_for_multi_surge(
                            selected_units, params, values, surge_specs, times
                        )

                    if 'error' in results:
                        st.error(results['error'])
                    else:
                        plot_surge_response(results)

                        # Store results in session state
                        st.session_state['last_surge_results'] = results
                else:
                    st.warning("Please define at least one surge event")

with tab4:
    st.header("Help & Documentation")

    help_tabs = st.tabs(["🚀 Quick Start", "📐 Model Configurations",
                         "📝 Equations", "📊 Variables", "💡 Tips"])

    with help_tabs[0]:
        st.markdown(QUICK_START_GUIDE)
    with help_tabs[1]:
        st.markdown(MODEL_CONFIGURATIONS)
    with help_tabs[2]:
        st.markdown(EQUATIONS_BY_MODEL)
        # Add your current equations
        st.markdown("### Your Current Equations")
        for eq in build_equations(selected_units):
            st.latex(eq)
    with help_tabs[3]:
        st.markdown(VARIABLE_DEFINITIONS)
    with help_tabs[4]:
        st.markdown(TIPS)


# =====================================================
# SIDEBAR INFORMATION
# =====================================================
render_sidebar_info(selected_units, params, values)

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.caption("Hospital Compartment Model Builder v2.0 | Built with Streamlit")






