import streamlit as st
import numpy as np
from typing import List, Dict, Any
import pandas as pd



def capacity_gap_assessment(unit_order, peak_extra_beds_per_comp, peak_extra_beds_total, params):
    #st.subheader("Current Hospital Status")


    # col1.markdown(
    #     "Enter the number of **currently available beds** in each unit to see if surge demand exceeds capacity.")


    available_beds = {}
    baseline_occupancy = {}

    st.markdown("### Capacity Gap Assessment")
    st.caption("Based on your current available beds and the calculated surge demand above")


    # Create editable fields for available beds
    st.markdown("**Enter your currently available surge beds:**")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

    for i, unit in enumerate(unit_order):
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
                f"Open/Staff {unit} Beds",
                min_value=0,
                value=int(base_val * 0.2) if base_val > 0 else 5,  # 20% buffer
                step=1,
                key=f"available_beds_{unit}",
                help=f"Current number of open/staff beds in {unit}. Baseline occupancy: {base_val:.1f}"
            )
    capacity_deficit = {}
    for unit in unit_order:
        available = available_beds.get(unit, 0)
        peak_extra = peak_extra_beds_per_comp[unit]
        if peak_extra > available:
            capacity_deficit[unit] = peak_extra - available
        else:
            capacity_deficit[unit] = 0
    has_deficit = any(v > 0 for v in capacity_deficit.values())

    if has_deficit:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.warning("⚠️ **Capacity Gaps Identified**")
            st.markdown("Additional beds required beyond available capacity:")

            gap_data = []
            for unit, deficit in capacity_deficit.items():
                if deficit > 0:
                    available = available_beds.get(unit, 0)
                    peak = peak_extra_beds_per_comp[unit]
                    gap_data.append({
                        "Unit": unit,
                        "Current Available": f"{available:.0f}",
                        "Peak Need": f"{peak:.0f}",
                        "Gap": f"{deficit:.0f}",
                        "Action": "🆘 Immediate need" if deficit > 0 else "✅ Sufficient"
                    })

            st.dataframe(
                pd.DataFrame(gap_data),
                column_config={
                    "Unit": "Unit",
                    "Current Available": st.column_config.TextColumn("Available", width="small"),
                    "Peak Need": st.column_config.TextColumn("Peak Need", width="small"),
                    "Gap": st.column_config.TextColumn("Gap", width="small"),
                    "Action": st.column_config.TextColumn("Status", width="medium")
                },
                hide_index=True,
                use_container_width=True
            )

        with col2:
            total_gap = sum(capacity_deficit.values())
            st.metric(
                label="🏗️ **Total Additional Beds Required**",
                value=f"{total_gap:.0f}",
                delta="above current capacity",
                help="Sum of all unit-level capacity gaps"
            )

            # Add recommendation
            st.info(
                f"💡 **Recommendation**: Consider activating {total_gap:.0f} additional surge beds "
                f"across {sum(1 for v in capacity_deficit.values() if v > 0)} unit(s) to meet peak demand."
            )
    else:
        st.success("✅ **Capacity Assessment: Adequate**")
        st.markdown(
            f"Your current available surge capacity is sufficient to handle the projected peak demand. "
            f"Maximum peak need is {peak_extra_beds_total:.0f} extra beds, which is within your available capacity."
        )

        # Show buffer calculation
        total_available = sum(available_beds.values())
        if total_available > 0:
            buffer = total_available - peak_extra_beds_total
            st.metric(
                label="📊 Capacity Buffer",
                value=f"{buffer:.0f} beds",
                delta=f"{buffer / peak_extra_beds_total * 100:.0f}% above peak need" if peak_extra_beds_total > 0 else None,
                help="Available capacity minus peak demand"
            )

    with st.expander("📖 Understanding These Metrics", expanded=False):
        st.markdown("""
          **Metric Definitions:**

          - **Peak Total Bed Demand**: Maximum number of additional beds needed at the worst point of the surge
          - **Surge Duration**: Total days from surge onset until the system returns to baseline
          - **Total Workload**: Cumulative excess bed-days (sum of all extra beds × days)
          - **Capacity Gap**: Difference between peak demand and available surge capacity

          **Interpretation:**
          - A positive capacity gap indicates immediate resource needs
          - Total workload helps estimate staffing and supply requirements
          - Surge duration informs how long resources will be needed
          """)


    #return available_beds, baseline_occupancy




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
    inpatient_units = [u for u in ['STEP', 'WARD', 'ICU'] if u in selected_units]
    #else:
        #from core.surge_analysis import transient_response_for_multi_surge, plot_surge_response, summary_metrics_surge_response

    if not inpatient_units:
        st.warning("Surge analysis requires at least one inpatient unit (WARD, STEP, or ICU)")
        return

    st.subheader("Define Surge Events")
    #with st.form(key="surge_definition_form"):

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
    col1, _ = st.columns([1,4])
    run_simulation = col1.button("🚀 Run Surge Analysis", type="primary", use_container_width=True)

    if run_simulation:
        dt = 1
        if surge_specs:
            times = np.arange(0, t_end + dt, dt)

            with st.spinner("Computing surge response..."):
                from core.surge_analysis import transient_response_for_multi_surge, plot_surge_response

                results = transient_response_for_multi_surge(
                    selected_units, params, values, surge_specs, times
                )

            if 'error' in results:
                st.error(f"❌ Simulation error: {results['error']}")
            else:
                #plot_surge_response(results)
                from core.surge_analysis import metrics_surge_response

                st.session_state['surge_results'] = results
                st.session_state['surge_metrics'] = metrics_surge_response(results)
                #st.success("✅ Simulation complete!")



                # Store results in session state
                st.session_state['last_surge_results'] = results
    if 'surge_results' in st.session_state:
        results = st.session_state['surge_results']
        #surge_metrics = st.session_state['surge_metrics']
        #st.subheader("📊 Surge Response")
        from core.surge_analysis import plot_surge_response, summary_metrics_surge_response
        plot_surge_response(results)
        surge_metrics = st.session_state['surge_metrics']
        summary_metrics_surge_response(results, surge_metrics)

        #st.markdown("---")
        #st.subheader("Step 3: Assess Your Capacity Gap")
        #st.caption("Now enter your available surge beds to see if you have enough capacity")

        capacity_gap_assessment(unit_order=results['unit_order'], peak_extra_beds_per_comp=surge_metrics['peak_extra_beds_per_comp'],
                               peak_extra_beds_total=surge_metrics['peak_extra_beds_total'], params=params)



    else:
        st.warning("Please define at least one surge event")
    return



