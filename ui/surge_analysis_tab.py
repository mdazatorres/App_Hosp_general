import streamlit as st
import numpy as np
from typing import List, Dict, Any


def current_hospital_occupancy_status(inpatient_units, params):
    st.subheader("Current Hospital Status")
    col1, col2, col3,col4 = st.columns([1,1,1,3])

    # col1.markdown(
    #     "Enter the number of **currently available beds** in each unit to see if surge demand exceeds capacity.")


    available_beds = {}
    baseline_occupancy = {}

    for i, unit in enumerate(inpatient_units):
        # Get baseline equilibrium for this unit
        base_val = params.get(f'{unit.lower()}_direct_admission_avg', 0)  # Fallback
        if unit == 'WARD':
            base_val = params.get('ward_direct_admission_avg', 0)
        elif unit == 'STEP':
            base_val = params.get('stepdown_direct_admission_avg', 0)
        elif unit == 'ICU':
            base_val = params.get('ICU_direct_admission_avg', 0)

        baseline_occupancy[unit] = base_val

        with [col1, col2, col3][i % 3]:
            available_beds[unit] = st.number_input(
                f"Available {unit} Beds",
                min_value=0,
                value=int(base_val * 0.2) if base_val > 0 else 5,  # 20% buffer
                step=1,
                key=f"available_beds_{unit}",
                help=f"Current number of empty beds in {unit}. Baseline occupancy: {base_val:.1f}"
            )
    return available_beds, baseline_occupancy

    st.divider()


def render_surge_analysis_tab(selected_units: List[str], params: Dict, values: Dict):
    st.header("Surge Analysis")
    st.markdown("""
        Analyze the system's response to multiple surge events in different units.
        Specify the timing, duration, and intensity of admission surges by unit.
        """)
    # Check prerequisites
    if not params or not values or not selected_units:
        st.warning("Please provide input values first")
        return
    else:
        from core.surge_analysis import transient_response_for_multi_surge, plot_surge_response, summary_metrics_surge_response
        inpatient_units = [u for u in ['STEP', 'WARD', 'ICU'] if u in selected_units]
        if not inpatient_units:
            st.warning("Surge analysis requires at least one inpatient unit (WARD, STEP, or ICU)")
        else:
            # Surge definition section

            available_beds, baseline_occupancy = current_hospital_occupancy_status(inpatient_units, params)

            st.subheader("Define Surge Events")
            surge_specs = {}

            for unit in inpatient_units:
                with st.expander(f"{unit} Unit Surges", expanded=(unit == inpatient_units[0])):
                    #st.markdown(f"Define surge events for **{unit}** unit")
                    col1, _, _ = st.columns(3)
                    n_surges = col1.number_input(f"Number of surge events for {unit}",
                        min_value=0, max_value=5, value=0, key=f"n_surges_{unit}")

                    unit_surges = []
                    for j in range(int(n_surges)):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            t_on = st.number_input(
                                f"Start day", min_value=0.0, value=5.0 + j * 10, step=1.0,
                                key=f"t_on_{unit}_{j}")
                        with col2:
                            t_off = st.number_input(
                                f"End day", min_value=t_on + 1, value=t_on + 5, step=1.0,
                                key=f"t_off_{unit}_{j}")
                        with col3:
                            amp = st.number_input(
                                f"Admissions per day", min_value=0.0, value=5.0, step=1.0,
                                key=f"amp_{unit}_{j}")
                        unit_surges.append((t_on, t_off, amp))

                    if unit_surges:
                        surge_specs[unit] = unit_surges

            # Simulation parameters
            st.subheader("Simulation Parameters")
            col1, col2 = st.columns(2)
            with col1:
                t_end = st.number_input(
                    "Simulation end time (days)",
                    min_value=10.0, max_value=365.0, value=50.0)

            # with col2:
            #     dt =  st.number_input(
            #         "Time step (days)",
            #         min_value=0.1, max_value=5.0, value=0.5
            #     )

            # Run button

            if st.button("🚀 Run Surge Analysis", type="primary"):
                dt = 1
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
                        summary_metrics_surge_response(results, available_beds, baseline_occupancy)

                        # Store results in session state
                        st.session_state['last_surge_results'] = results
                else:
                    st.warning("Please define at least one surge event")
    return