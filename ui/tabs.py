# ui/tabs.py
import streamlit as st
import pandas as pd
from typing import List, Dict
from core.equation_builder import build_equations
from core.constants import DATA_DICTIONARY


def render_model_summary_tab(selected_units: List[str], flows: List[tuple], required_data: set):
    """Render the Model Summary tab"""
    #st.header("Model Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Selected Units")
        for unit in selected_units:
            st.write(f"✅ {unit}")

    with col2:
        st.subheader("Hospital Flow Structure")
        if flows:
            # Split flows into two columns if more than 4
            if len(flows) > 4:
                # Split the flows list into two halves
                mid = len(flows) // 2 + (len(flows) % 2)
                flows_col1, flows_col2 = flows[:mid], flows[mid:]

                # Create nested columns
                flow_col1, flow_col2 = st.columns(2)
                with flow_col1:
                    for a, b in flows_col1:
                        st.write(f"  • {a} → {b}")
                with flow_col2:
                    for a, b in flows_col2:
                        st.write(f"  • {a} → {b}")
            else:
                for a, b in flows:
                    st.write(f"  • {a} → {b}")
        else:
            st.write("No flows defined")

    st.divider()
    _render_data_dictionary(required_data)
    st.divider()
    _render_ode_system(selected_units)


def _render_data_dictionary(required_data: set):
    """Helper to render data dictionary"""
    st.subheader("Required Data Inputs")
    if not required_data:
        st.write("No data inputs required")
        return

    data_list = sorted(required_data)
    # Quick reference
    cols = st.columns(3)
    badge_colors = {'ED': '🔴', 'WARD': '🟢', 'STEP': '🔵', 'ICU': '🟣'}

    for i, data in enumerate(data_list):
        category = DATA_DICTIONARY.get(data, {}).get('category', 'Unknown')
        badge = badge_colors.get(category, '⚪')
        cols[i % 3].write(f"{badge} {data}")

    with st.expander("📚 Click to see detailed variable descriptions", expanded=False):
        _render_data_dictionary_tabs(data_list)



def _render_data_dictionary_tabs(data_list: List[str]):
    """Render tabs for each unit"""
    # Get unique categories from data_list
    categories = set()
    for var in data_list:
        if var in DATA_DICTIONARY:
            categories.add(DATA_DICTIONARY[var]['category'])

    if not categories:
        st.info("No categorized data available")
        return

    unit_tabs = st.tabs(list(categories))

    for tab, category in zip(unit_tabs, categories):
        with tab:
            unit_vars = [v for v in data_list
                         if v in DATA_DICTIONARY
                         and DATA_DICTIONARY[v]['category'] == category]

            if unit_vars:
                table_data = [{'Variable': DATA_DICTIONARY[var]['name'],
                    'Description': DATA_DICTIONARY[var]['description'],
                    'Unit': DATA_DICTIONARY[var]['unit']
                } for var in sorted(unit_vars)]

                st.dataframe(
                    pd.DataFrame(table_data),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Variable": st.column_config.TextColumn(width="medium"),
                        "Description": st.column_config.TextColumn(width="large"),
                        "Unit": st.column_config.TextColumn(width="small")})
            else:
                st.info(f"No variables defined for {category}")


def _render_ode_system(units: List[str]):
    """Render ODE equations"""
    st.subheader("ODE System")
    st.write("The following ordinary differential equations (ODEs) describe patient flow through "
             "the selected interconnected clinical units. For a detailed explanation of each equation"
             " and model configuration, please refer to the **Documentation** tab.")
    equations = build_equations(units)
    for eq in equations:
        st.latex(eq)


def render_equilibrium_tab(selected_units: List[str], params: Dict, values: Dict):
    """Render the Equilibrium tab"""
    st.header("Equilibrium Analysis")

    if st.button("🔄 Calculate Equilibrium", type="primary"):
        if params and values:
            from core.equilibrium_solver import solve_equilibrium
            equilibrium = solve_equilibrium(selected_units, params, values)

            # ADD THIS PART - Show plots if we have uploaded data
            if equilibrium and st.session_state.get('uploaded_df_for_plot') is not None:
                from ui.visualizations import (plot_units_comparison, plot_utilization_metrics)

                df = st.session_state['uploaded_df_for_plot']

                st.divider()
                st.subheader("📊 Comparison with Historical Data")

                # Create tabs for different visualizations
                viz_tab1, viz_tab2 = st.tabs(["📈 Occupancy Trends", "📋 Summary Metrics"])

                with viz_tab1:
                    plot_units_comparison(df, equilibrium, selected_units)

                with viz_tab2:
                    plot_utilization_metrics(df, equilibrium, selected_units)

            elif equilibrium:
                st.info("ℹ️ Upload Excel data to see comparison with historical trends")
        else:
            st.warning("Please provide input values first")


def render_dynamics_tab(selected_units: List[str], params: Dict, values: Dict):
    """Render the Dynamics tab"""
    st.header("Time Dynamics Simulation")

    simulation_days = st.number_input("Simulation days", min_value=1, max_value=365, value=30)

    if st.button("▶️ Run Simulation", type="primary"):
        if params and values and len(selected_units) > 0:
            from core.dynamics_simulator import simulate_dynamics
            simulate_dynamics(selected_units, params, values, days=simulation_days)
        else:
            st.warning("Please provide input values first")

    st.info("""
        This simulation shows how patient numbers evolve over time.
        The system should reach equilibrium after sufficient time.

        **Initial conditions:**
        - Waiting area: 50 patients
        - Treatment area: 20 patients
        - Ward boarding: 30 patients
        - Step-down boarding: 15 patients
        - ICU boarding: 10 patients
    """)

# chek if this function is necessary

def render_sidebar_info(selected_units: List[str], params: Dict, values: Dict):
    """Render sidebar information"""
    st.sidebar.divider()
    st.sidebar.markdown(f"**Current configuration:** {', '.join(selected_units) if selected_units else 'None'}")
    st.sidebar.markdown(f"**Number of parameters:** {len(params)}")
    st.sidebar.markdown(f"**Number of input values:** {len(values)}")