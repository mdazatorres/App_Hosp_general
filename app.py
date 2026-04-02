import streamlit as st
from core.equation_builder import build_equations
from core.data_manager import get_flows, get_selected_units, get_required_data
from core.data_processor import process_input_data
from utils.session_manager import initialize_session, update_current_params
from ui.tabs import (render_model_summary_tab, render_equilibrium_tab, render_dynamics_tab, render_sidebar_info)
from ui.surge_analysis_tab import render_surge_analysis_tab
from ui.help_content import (QUICK_START_GUIDE, MODEL_INFO)
import numpy as np
# Add this to your imports if not already there
from ui.visualizations import (
    plot_units_comparison,
    plot_utilization_metrics)

# Page configuration
st.set_page_config(layout="wide", page_title="Hospital Surge Capacity Planner")
st.title("🏥 Hospital Surge Capacity Planner")

# Initialize session state
initialize_session()

# =====================================================
# GET USER CONFIGURATION
# =====================================================
selected_units = get_selected_units()

st.sidebar.header("Hospital operational data")
mode = st.sidebar.radio("Provide values:", ["Manual entry", "Upload Excel (daily data)"])

required_data = get_required_data(selected_units, mode)
flows = get_flows(selected_units)

# =====================================================
# PROCESS INPUT DATA
# =====================================================
values, params = process_input_data(required_data, selected_units, mode) # here I compute the parameters from excel or manual entry
update_current_params(params)

# =====================================================
# CREATE TABS
# =====================================================
tab1, tab2, tab3,   tab4 = st.tabs(["📚 Documentation","📋 Model Summary","⚖️ Equilibrium", "📑 Scenario Analysis"])

with tab1:
    #st.header("Documentation")

    help_tabs = st.tabs(["Quick Start", "Model Documentation"])

    with help_tabs[0]:
        st.markdown(QUICK_START_GUIDE)
    with help_tabs[1]:
        st.markdown(MODEL_INFO, unsafe_allow_html=True)

with tab2:
    render_model_summary_tab(selected_units, flows, required_data)

#with tab2:
#    render_parameters_tab(params, values)
# This just for test any mistake

with tab3:
    render_equilibrium_tab(selected_units, params, values)

# with tab4:
#     render_dynamics_tab(selected_units, params, values)

with tab4:
    render_surge_analysis_tab(selected_units, params, values)



    # with help_tabs[2]:
    #     st.markdown(EQUATIONS_BY_MODEL)
    #     # Add your current equations
    #     st.markdown("### Your Current Equations")
    #     for eq in build_equations(selected_units):
    #         st.latex(eq)
    # with help_tabs[3]:
    #     st.markdown(VARIABLE_DEFINITIONS)
    # with help_tabs[4]:
    #     st.markdown(TIPS)


# =====================================================
# SIDEBAR INFORMATION
# =====================================================
render_sidebar_info(selected_units, params, values)

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.caption("Hospital Compartment Model Builder v2.0 | Built with Streamlit")






