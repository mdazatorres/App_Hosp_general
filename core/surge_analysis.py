#from data_params import *
from scipy.linalg import expm
import streamlit as st
import pandas as pd
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go
from plotly.subplots import make_subplots  # Add this line
import plotly.express as px
from typing import Dict, List, Tuple, Optional, Any



def build_jacobian(params, selected_units):
    """
    Build the Jacobian matrix for the inpatient units at equilibrium.

    The Jacobian represents the linearized system:
    dX/dt = J * X, where X = [STEP, WARD, ICU] (in that order)

    Parameters:
    -----------
    params : Dict
        Dictionary of model parameters (must contain all relevant rates)
    selected_units : List[str]
        List of selected units (e.g., ['ED', 'WARD', 'STEP', 'ICU'])

    Returns:
    --------
    J : np.ndarray or None
        Jacobian matrix (n x n where n = number of inpatient units)
    eigenvalues : np.ndarray or None
        Eigenvalues of the Jacobian
    unit_order : List[str]
        Order of units in the Jacobian matrix rows/columns
    """

    # Determine which inpatient units are present
    inpatient_units = []
    for unit in ['STEP', 'WARD', 'ICU']:
        if unit in selected_units:
            inpatient_units.append(unit)

    n = len(inpatient_units)
    if n == 0:
        return None, None, []

    # Initialize Jacobian
    J = np.zeros((n, n))

    # Create mapping from unit to index
    unit_to_idx = {unit: i for i, unit in enumerate(inpatient_units)}

    # Build Jacobian based on which units are present
    for i, unit in enumerate(inpatient_units):
        if unit == "STEP":
            # d(STEP)/dt terms - outflows (negative on diagonal)
            J[i, i] -= params.get("step_discharge_rate", 0)  # Always discharge

            # Only subtract transfer rates if destination units exist
            if "ICU" in inpatient_units:
                J[i, i] -= params.get("step_to_ICU_rate", 0)
                j = unit_to_idx["ICU"]
                J[i, j] += params.get("ICU_to_step_rate", 0)

            if "WARD" in inpatient_units:
                J[i, i] -= params.get("step_to_ward_rate", 0)


        elif unit == "WARD":
            # d(WARD)/dt terms - outflows (negative on diagonal)
            J[i, i] -= params.get("ward_discharge_rate", 0)  # Always discharge

            # Only subtract transfer rates if destination units exist
            if "ICU" in inpatient_units:
                J[i, i] -= params.get("ward_to_ICU_rate", 0)

            # Inflows from other units (positive off-diagonal) # From ICU to WARD

                j = unit_to_idx["ICU"]
                J[i, j] += params.get("ICU_to_ward_rate", 0)

            # From STEP to WARD
            if "STEP" in inpatient_units:
                j = unit_to_idx["STEP"]
                J[i, j] += params.get("step_to_ward_rate", 0)

        elif unit == "ICU":
            # d(ICU)/dt terms - outflows (negative on diagonal)
            J[i, i] -= params.get("ICU_discharge_rate", 0)  # Always discharge

            # Only subtract transfer rates if destination units exist
            if "WARD" in inpatient_units:
                J[i, i] -= params.get("ICU_to_ward_rate", 0)

            if "STEP" in inpatient_units:
                J[i, i] -= params.get("ICU_to_step_rate", 0)

            # Inflows from other units (positive off-diagonal)
            # From WARD to ICU
            if "WARD" in inpatient_units:
                j = unit_to_idx["WARD"]
                J[i, j] += params.get("ward_to_ICU_rate", 0)

            # From STEP to ICU
            if "STEP" in inpatient_units:
                j = unit_to_idx["STEP"]
                J[i, j] += params.get("step_to_ICU_rate", 0)

    # Calculate eigenvalues
    eigenvalues = np.linalg.eigvals(J)

    return J, eigenvalues, inpatient_units




def solve_equilibrium_with_surge(units: List[str], params: Dict, values: Dict,
                                 surge_amplitude: Dict[str, float]) -> Dict:
    """
    Solve equilibrium with surge amplitude added to direct admissions.

    Parameters:
    -----------
    units : List[str]
        Selected hospital units
    params : Dict
        Model parameters
    values : Dict
        Input values
    surge_amplitude : Dict[str, float]
        Surge amplitudes for each unit {'WARD': val, 'STEP': val, 'ICU': val}

    Returns:
    --------
    Dict : Equilibrium results
    """
    # This is a modified version that adds surge to direct admissions
    equilibrium = {}

    # ===== ED EQUILIBRIUM =====
    if "ED" in units:
        lambda_arr = float(params.get("daily_ED_arrivals_avg", 100))
        sigma = params.get("sigma", 2.0)
        omega = params.get("omega", 0.2)
        gamma = params.get("gamma", 1.0)

        # Waiting steady state
        W_eq = lambda_arr / max((sigma + omega), 1e-9)
        S_eq = sigma * W_eq / max(gamma, 1e-9)

        equilibrium["Waiting (W)"] = W_eq
        equilibrium["Treatment (S)"] = S_eq

        # Boarding areas
        if "WARD" in units and "xi_ward" in params:
            B_ward = params["pED_to_ward"] * gamma * S_eq / max(params["xi_ward"], 1e-9)
            equilibrium["Ward Boarding"] = B_ward
        else:
            B_ward = 0

        if "STEP" in units and "xi_step" in params:
            B_step = params["pED_to_step"] * gamma * S_eq / max(params["xi_step"], 1e-9)
            equilibrium["Step Boarding"] = B_step
        else:
            B_step = 0

        if "ICU" in units and "xi_ICU" in params:
            B_ICU = params["pED_to_ICU"] * gamma * S_eq / max(params["xi_ICU"], 1e-9)
            equilibrium["ICU Boarding"] = B_ICU
        else:
            B_ICU = 0

    # ===== INPATIENT LINEAR SYSTEM with SURGE =====
    inpatient_units = [u for u in ["STEP", "WARD", "ICU"] if u in units]

    if len(inpatient_units) > 0:
        n = len(inpatient_units)
        A = np.zeros((n, n))
        b = np.zeros(n)
        unit_index = {u: i for i, u in enumerate(inpatient_units)}

        for u in inpatient_units:
            i = unit_index[u]

            if u == "STEP":
                # Add surge to direct admissions
                direct = float(params.get("stepdown_direct_admission_avg", 0)) + surge_amplitude.get('STEP', 0)
                transfer = float(params.get("stepdown_transfer_admission_avg", 0))
                boarding = params.get('xi_step', 0) * B_step if 'ED' in units else 0
                mu = params.get("step_discharge_rate", 0)

                A[i, i] += mu
                b[i] = direct + transfer + boarding

                if "ICU" in inpatient_units:
                    j = unit_index["ICU"]
                    rho = params.get("ICU_to_step_rate", 0)
                    A[i, j] -= rho
                    A[j, j] += rho

            if u == "WARD":
                # Add surge to direct admissions
                direct = float(params.get("ward_direct_admission_avg", 0)) + surge_amplitude.get('WARD', 0)
                transfer = float(params.get("ward_transfer_admission_avg", 0))
                boarding = params.get('xi_ward', 0) * B_ward if 'ED' in units else 0
                mu = params.get("ward_discharge_rate", 0)

                A[i, i] += mu
                b[i] = direct + transfer + boarding

                if "ICU" in inpatient_units:
                    j = unit_index["ICU"]
                    rho = params.get("ICU_to_ward_rate", 0)
                    A[i, j] -= rho
                    A[j, j] += rho

                if "STEP" in inpatient_units:
                    j = unit_index["STEP"]
                    rho = params.get("step_to_ward_rate", 0)
                    A[i, j] -= rho
                    A[j, j] += rho

            if u == "ICU":
                # Add surge to direct admissions
                direct = float(params.get("ICU_direct_admission_avg", 0)) + surge_amplitude.get('ICU', 0)
                transfer = float(params.get("ICU_transfer_admission_avg", 0))
                boarding = params.get('xi_ICU', 0) * B_ICU if 'ED' in units else 0
                mu = params.get("ICU_discharge_rate", 0)

                A[i, i] += mu
                b[i] = direct + transfer + boarding

                if "WARD" in inpatient_units:
                    j = unit_index["WARD"]
                    rho = params.get("ward_to_ICU_rate", 0)
                    A[i, j] -= rho
                    A[j, j] += rho

                if "STEP" in inpatient_units:
                    j = unit_index["STEP"]
                    rho = params.get("step_to_ICU_rate", 0)
                    A[i, j] -= rho
                    A[j, j] += rho

        try:
            sol = np.linalg.solve(A, b)
            for u in inpatient_units:
                equilibrium[u] = sol[unit_index[u]]
        except np.linalg.LinAlgError:
            st.error("Equilibrium matrix is singular. Check transfer rates.")
            return {}

    return equilibrium



def transient_response_for_multi_surge(units: List[str], params: Dict, values: Dict,
                                       surge_specs: Dict[str, List[Tuple[float, float, float]]],
                                       times: np.ndarray) -> Dict[str, Any]:
    """
    Compute transient response to multiple surge events using linearized dynamics.

    Parameters:
    -----------
    units : List[str]
        Selected hospital units
    params : Dict
        Model parameters
    values : Dict
        Input values
    surge_specs : Dict[str, List[Tuple[float, float, float]]]
        Dictionary with keys 'WARD', 'STEP', 'ICU' and values as lists of
        (start_time, end_time, amplitude) tuples
    times : np.ndarray
        Time points for evaluation

    Returns:
    --------
    Dict with keys:
        'times': time points
        'x_ts': trajectory array (n_times x n_units)
        'x0': baseline equilibrium
        'extra_beddays_total': total extra bed-days across all units
        'extra_beddays_per_comp': dict of extra bed-days per unit
        'eigvals': eigenvalues of Jacobian
    """

    # Baseline equilibrium (no surge)
    surge_amplitude = {'WARD': 0, 'STEP': 0, 'ICU': 0}
    eq_baseline = solve_equilibrium_with_surge(units, params, values, surge_amplitude)

    # Get inpatient units in consistent order
    inpatient_units = [u for u in ['STEP', 'WARD', 'ICU'] if u in units]
    n_units = len(inpatient_units)

    if n_units == 0:
        return {'error': 'No inpatient units selected'}

    # Extract baseline values in correct order
    x0 = np.array([eq_baseline.get(u, 0) for u in inpatient_units])

    # Build Jacobian
    J, eigvals, _ = build_jacobian(params, units)

    # Initialize trajectory
    x_ts = np.zeros((len(times), n_units))
    x_ts[0] = x0.copy()

    # Precompute equilibrium shifts for each surge event
    surge_deltas = []  # List of (t_on, t_off, delta_eq)

    for comp, windows in surge_specs.items():
        if comp not in inpatient_units:
            continue

        for (t_on, t_off, amp) in windows:
            # Create surge amplitude dict with only this event
            surge_dict = {'WARD': 0, 'STEP': 0, 'ICU': 0}
            surge_dict[comp] = amp

            # Compute equilibrium with this surge
            eq_surge = solve_equilibrium_with_surge(units, params, values, surge_dict)

            # Extract values in correct order
            x_surge = np.array([eq_surge.get(u, 0) for u in inpatient_units])

            # Store delta from baseline
            surge_deltas.append((t_on, t_off, x_surge - x0))

    # Superposition of linear responses
    for k, t in enumerate(times[1:], 1):
        z = np.zeros(n_units)

        for (t_on, t_off, delta_eq) in surge_deltas:
            if t < t_on:
                continue
            elif t_on <= t <= t_off:
                # During surge
                tau = t - t_on
                z += (np.eye(n_units) - expm(J * tau)).dot(delta_eq)
            else:
                # After surge
                tau_s = t_off - t_on
                z_T = (np.eye(n_units) - expm(J * tau_s)).dot(delta_eq)
                z += expm(J * (t - t_off)).dot(z_T)

        x_ts[k] = x0 + z
    #------------------ solve this trapz instead trapezoid
    # Calculate extra bed-days
    #extra_beddays_total = np.trapezoid(np.sum(x_ts - x0, axis=1), times)
    extra_beddays_total = np.trapz(np.sum(x_ts - x0, axis=1), times)

    extra_beddays_per_comp = {}
    for i, unit in enumerate(inpatient_units):
        #extra_beddays_per_comp[unit] = np.trapezoid(x_ts[:, i] - x0[i], times)
        extra_beddays_per_comp[unit] = np.trapz(x_ts[:, i] - x0[i], times)

    # Pack results
    results = {
        'times': times,
        'x_ts': x_ts,
        'x0': x0,
        'unit_order': inpatient_units,
        'extra_beddays_total': extra_beddays_total,
        'extra_beddays_per_comp': extra_beddays_per_comp,
        'eigvals': eigvals,
        'surge_specs': surge_specs }

    return results


def plot_surge_response1(results: Dict[str, Any]):
    """
    Plot surge response results using Plotly.

    Parameters:
    -----------
    results : Dict
        Results from transient_response_for_multi_surge
    """
    times = results['times']
    x_ts = results['x_ts']
    x0 = results['x0']
    unit_order = results['unit_order']
    surge_specs = results.get('surge_specs', {})

    # Calculate peak demands
    extra_beds_over_time = x_ts - x0
    peak_extra_beds_per_comp = {}
    for i, unit in enumerate(unit_order):
        peak_extra_beds_per_comp[unit] = float(np.max(extra_beds_over_time[:, i]))

    # Create subplots
    fig = make_subplots(
        rows=len(unit_order),
        cols=1,
        subplot_titles=[f"{unit} Unit Response" for unit in unit_order],
        vertical_spacing=0.1,
        shared_xaxes=True,
        specs=[[{"secondary_y": True}] for _ in range(len(unit_order))]  # Add secondary y-axis for each row
    )

    colors = {'WARD': '#4ecdc4', 'STEP': '#45b7d1', 'ICU': '#96ceb4'}
    extra_colors = {'WARD': '#2c8c7a', 'STEP': '#2a6f8a', 'ICU': '#5a8a6e'}  # Darker shade

    for i, unit in enumerate(unit_order):
        # Plot trajectory
        fig.add_trace(go.Scatter(x=times, y=x_ts[:, i], mode='lines',
                name=f'{unit}', line=dict(color=colors.get(unit, '#888888'), width=3),
                showlegend=True), row=i + 1, col=1)

        # Plot baseline
        fig.add_trace(go.Scatter(x=times, y=[x0[i]] * len(times), mode='lines',
                name=f'{unit} Baseline', line=dict(color='red', width=2, dash='dash'),
                showlegend=True), row=i + 1, col=1)

        # --- extra beds (right axis, starts at 0) ---
        fig.add_trace(go.Scatter(x=times, y=x_ts[:, i]-x0[i], mode="lines",
                                  line=dict(color=extra_colors.get(unit, '#666666'), width=2, dash="dot"),
                                 visible="legendonly",
                                 showlegend=False), row=i + 1, col=1, secondary_y=True)
        fig.update_yaxes(title_text="Extra beds", secondary_y=True,
                         row=i + 1, col=1, rangemode="tozero")

        # Shade surge periods
        if unit in surge_specs:
            for t_on, t_off, amp in surge_specs[unit]:
                fig.add_vrect(x0=t_on, x1=t_off, fillcolor="rgba(255, 0, 0, 0.1)",
                    layer="below", line_width=0, row=i + 1, col=1)

                # Add peak annotation
        peak_idx = np.argmax(extra_beds_over_time[:, i])
        peak_time = times[peak_idx]
        peak_value = x_ts[peak_idx, i]

        fig.add_annotation(x=peak_time, y=peak_value,
            text=f"Peak: {peak_value:.1f}", showarrow=True,
            arrowhead=2, arrowcolor=colors.get(unit, '#888888'),
            arrowsize=1, arrowwidth=2,ax=20,ay=-30,
            row=i + 1, col=1)
        fig.update_yaxes(title_text="Patients", row=i + 1, col=1)

    fig.update_xaxes(title_text="Time (days)", row=len(unit_order), col=1)

    fig.update_layout(height=300 * len(unit_order),
        title_text="Surge Response Analysis",
        hovermode='x unified',
        showlegend=True)

    st.plotly_chart(fig, use_container_width=True)





def plot_surge_response(results: Dict[str, Any]):

    times = results['times']
    x_ts = results['x_ts']
    x0 = results['x0']
    unit_order = results['unit_order']
    surge_specs = results.get('surge_specs', {})

    fig = make_subplots(
        rows=len(unit_order),
        cols=1,
        subplot_titles=[f"{unit} Unit Response" for unit in unit_order],
        vertical_spacing=0.1,
        shared_xaxes=True
    )

    colors = {'WARD': '#4ecdc4', 'STEP': '#45b7d1', 'ICU': '#96ceb4'}

    for i, unit in enumerate(unit_order):

        baseline = np.full(len(times), x0[i])
        extra = x_ts[:, i] - x0[i]

        # --- Baseline
        fig.add_trace(
            go.Scatter(
                x=times,
                y=baseline,
                mode='lines',
                name=f'{unit} Baseline',
                line=dict(color='red', dash='dash'),
                showlegend=(i == 0),
                hovertemplate="Baseline: %{y:.2f}<extra></extra>"
            ),
            row=i + 1, col=1
        )

        # --- Occupancy + shaded extra beds
        fig.add_trace(
            go.Scatter(
                x=times,
                y=x_ts[:, i],
                mode='lines+markers',
                name=f'{unit}',
                line=dict(color=colors.get(unit, '#888888'), width=3),
                fill='tonexty',
                fillcolor='rgba(0, 0, 0, 0.)',
                showlegend=(i == 0),
                customdata=np.stack([baseline, extra], axis=-1),
                hovertemplate=(
                    "Day %{x}<br>"
                    "Patients: %{y:.2f}<br>"
                    "Extra Beds: %{customdata[1]:.2f}"
                    "<extra></extra>"
                )
            ),
            row=i + 1, col=1
        )


        # --- Surge shading
        if unit in surge_specs:
            for t_on, t_off, amp in surge_specs[unit]:
                fig.add_vrect(
                    x0=t_on, x1=t_off,
                    fillcolor="rgba(255,0,0,0.1)",
                    layer="below",
                    line_width=0,
                    row=i + 1, col=1
                )

        # --- Peak annotation
        peak_idx = np.argmax(extra)
        fig.add_annotation(
            x=times[peak_idx],
            y=x_ts[peak_idx, i],
            text=f"Peak Extra: {extra[peak_idx]:.1f}",
            showarrow=True,
            arrowhead=2,
            row=i + 1, col=1
        )

        fig.update_yaxes(title_text="Patients", row=i + 1, col=1)

    fig.update_xaxes(title_text="Time (days)", row=len(unit_order), col=1)

    fig.update_layout(
        height=320 * len(unit_order),
        title="Surge Response Analysis",
        hovermode='x unified'  # 🔥 synchronized daily view
    )

    st.plotly_chart(fig, use_container_width=True)


def summary_metrics_surge_response(results: Dict[str, Any]):
    """
    Plot surge response results using Plotly.

    Parameters:
    -----------
    results : Dict
        Results from transient_response_for_multi_surge
    """
    # --------------- Compute transient system response to multiple surge events ------
    times = results['times']
    x_ts = results['x_ts']  # Time series of state variables (beds by unit)
    x0 = results['x0']      # Baseline equilibrium (no-surge steady state)
    unit_order = results['unit_order']


    # Calculate peak demands
    extra_beds_over_time = x_ts - x0 # Compute daily excess bed occupancy relative to baseline


    # -------------- Apply threshold to the time series output --------------
    # We define "active surge impact" as any time when at least one unit exceeds the baseline by more than the specified threshold.

    threshold = 0.1  # minimum extra beds considered meaningful
    max_extra = np.max(extra_beds_over_time, axis=1) # Maximum excess occupancy across units at each time point
    active_idx = np.where(max_extra >= threshold)[0] # Indices where the system is still above the threshold

    # Last time index with meaningful surge impact
    if len(active_idx) > 0:
        t_cut = active_idx[-1] + 1
    else:
        t_cut = 1   # No meaningful deviation from equilibrium detected
    # Truncate the time series to exclude periods where excess occupancy is negligible (< threshold).
    # All downstream workload and cost calculations are based on this truncated series.
    # we haven't yet used these for plot. check if we want to add them
    times_plot = times[:t_cut]
    x_ts_plot= x_ts[:t_cut]


    peak_extra_beds_total = float(np.max(np.sum(extra_beds_over_time, axis=1)))
    peak_extra_beds_per_comp = {}
    for i, unit in enumerate(unit_order):
        peak_extra_beds_per_comp[unit] = float(np.max(extra_beds_over_time[:, i]))


    # Display metrics
    col1, col2= st.columns(2)
    with col1:
        st.write("### 🏥 Peak Additional Bed Requirements")
        st.metric("Total Extra Beds Needed", f"{peak_extra_beds_total:.1f}", delta=None)
        st.markdown("**By unit:**")
        for unit in unit_order:
            peak = peak_extra_beds_per_comp[unit]
            baseline = x0[unit_order.index(unit)]
            pct_increase = (peak / baseline * 100) if baseline > 0 else 0
            st.markdown(f"- **{unit}**: {peak:.1f} extra "f"({pct_increase:.0f}% above baseline)")

    # with col2:
    #     max_excess = np.max(np.sum(x_ts - x0, axis=1))
    #     st.metric("Peak Excess Patients", f"{max_excess:.1f}")

    with col2:
        st.write("### 📊 Cumulative Bed-Days (Total Workload)")

        # st.metric("Total Extra Bed-Days", f"{results['extra_beddays_total']:.1f}")
        # st.markdown("**By unit:**")
        # for unit in unit_order:
        #     st.write(f"- {unit}: {results['extra_beddays_per_comp'][unit]:.1f}")


        extra_beds_over_time_cut = extra_beds_over_time[:t_cut]
        extra_beddays_per_comp_cut = {comp: extra_beds_over_time_cut[:, j].sum() for j, comp in enumerate(unit_order)}
        extra_beddays_total_cut = sum(extra_beddays_per_comp_cut.values()) # Total system-wide bed-days

        st.metric("Extra Bed-Days (Total)", f"{extra_beddays_total_cut:.1f}")
        st.markdown("**By unit:**")
        for unit, beddays in extra_beddays_per_comp_cut.items():
            st.write(f"- {unit}: {beddays:.1f} bed-days")

    # Time to return to baseline (within 5%)
    # threshold = 0.05 * np.sum(x0)
    # close_enough = np.where(np.sum(np.abs(x_ts - x0), axis=1) < threshold)[0]
    # if len(close_enough) > 0:
    #     recovery_time = times[close_enough[0]]
    # else:
    #     recovery_time = times[-1]
    # st.metric("Recovery Time (days)", f"{recovery_time:.1f}")
    #
    # # Extra bed-days per unit

    # all the information here is correct I need to organize it


# =============================================================================
# EXAMPLE TEST MODULE
# =============================================================================

def run_example_test():
    from aux_functions import  transient_response_for_multi_surge_ex

    """
    Run an example test of the surge analysis module.
    This can be called independently to validate the module before integration.
    """
    print("=" * 60)
    print("SURGE ANALYSIS MODULE - EXAMPLE TEST")
    print("=" * 60)

    # Create mock parameters (similar to what the app would provide)
    params = {
        # ED parameters
        'daily_ED_arrivals_avg': 270.82,
        'sigma': 12.78,
        'omega': 0.34,
        'gamma': 9.056,
        'pED_to_step': 0.005464344528170069,
        'pED_to_ward': 0.1329074970474242,
        'pED_to_ICU': 0.024976296222366384,
        'xi_ICU': 1.4788523039502726,
        'xi_ward': 1.4788523039502726,
        'xi_step': 1.4788523039502726,

        # Ward parameters
        'ward_discharge_rate': 0.165809381385132,
        'ward_to_ICU_rate': 0.0074498912644547065,
        'ward_direct_admission_avg': 9.28,
        'ward_transfer_admission_avg': 7.64,

        # Step-down parameters
        'step_discharge_rate': 0.27873563218390807,
        'step_to_ICU_rate': 0.09299895506792058,
        'step_to_ward_rate': 0.42,
        'stepdown_direct_admission_avg': 5.28,
        'stepdown_transfer_admission_avg': 0.60,

        # ICU parameters
        'ICU_discharge_rate': 0.03964318285453716,
        'ICU_to_ward_rate': 0.16638166894664844,
        'ICU_to_step_rate': 0.0013109895120839033,
        'ICU_direct_admission_avg': 2.00,
        'ICU_transfer_admission_avg': 3.37,
    }

    values = {}  # Not needed for this test
    units = ['ED', 'WARD', 'STEP', 'ICU']  # Full hospital

    # Define surge events
    surge_specs = {
        'STEP': [(3, 7, 2), (8, 10, 5)],  # Two surges in step-down
        'WARD': [(1, 10, 2), (5, 20, 1)],  # Two surges in ward
        'ICU': [(3, 4, 1)]  # One surge in ICU
    }

    # Time grid
    t_end = max(w[1] for comp in surge_specs.values() for w in comp) + 30
    times = np.arange(0, t_end + 1, 0.5)  # 0.5 day resolution

    print(f"\nSurge specifications:")
    for comp, windows in surge_specs.items():
        print(f"  {comp}: {windows}")

    print(f"\nTime grid: 0 to {t_end} days, {len(times)} points")

    # Compute baseline equilibrium
    surge_amplitude = {'WARD': 0, 'STEP': 0, 'ICU': 0}
    eq_baseline = solve_equilibrium_with_surge(units, params, values, surge_amplitude)

    print(f"\nBaseline equilibrium:")
    for key in ['WARD', 'STEP', 'ICU']:
        if key in eq_baseline:
            print(f"  {key}: {eq_baseline[key]:.2f}")

    # Compute surge response
    results = transient_response_for_multi_surge(units, params, values, surge_specs, times)

    print(f"\nSurge response results:")
    print(f"  Total extra bed-days: {results['extra_beddays_total']:.2f}")
    print(f"  Extra bed-days by unit:")
    for unit, val in results['extra_beddays_per_comp'].items():
        print(f"    {unit}: {val:.2f}")

    # Create simple matplotlib plot for validation
    #try:
        #uncomente this to see the plot
        # import matplotlib.pyplot as plt
        #
        # fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
        #
        # for i, unit in enumerate(results['unit_order']):
        #     axes[i].plot(results['times'], results['x_ts'][:, i], 'b-', linewidth=2, label='Response')
        #     axes[i].axhline(y=results['x0'][i], color='r', linestyle='--', label='Baseline')
        #     axes[i].set_ylabel(f'{unit} (patients)')
        #     axes[i].legend()
        #     axes[i].grid(alpha=0.3)
        #
        #     # Shade surge periods
        #     if unit in surge_specs:
        #         for t_on, t_off, amp in surge_specs[unit]:
        #             axes[i].axvspan(t_on, t_off, alpha=0.2, color='red')

        # axes[-1].set_xlabel('Time (days)')
        # plt.suptitle('Surge Response Test')
        # plt.tight_layout()
        # plt.show()

    # except ImportError:
    #     print("\nMatplotlib not available for plotting")

    print("\n" + "=" * 60)
    print("TEST COMPLETE - Module ready for integration")
    print("=" * 60)


    print("\n" + "=" * 60)
    print("Validate with the original functions")
    params_formatted = {'sigma': params["sigma"], 'omega': params["omega"], 'gamma': params["gamma"],
                        'pED_Hs': params["pED_to_step"], 'pED_Hm': params["pED_to_ward"],
                        'pED_ICU': params["pED_to_ICU"],
                        'xi_I': params["xi_ICU"], 'xi_Hm': params["xi_ward"], 'xi_Hs': params["xi_step"],
                        'varphi_I': params["step_to_ICU_rate"], 'varphi_D': params["step_discharge_rate"],
                        'varphi_Hm': params["step_to_ward_rate"], 'psi_I': params["ward_to_ICU_rate"],
                        'psi_D': params["ward_discharge_rate"],
                        'eps_Hs': params["ICU_to_step_rate"], 'eps_Hm': params["ICU_to_ward_rate"],
                        'eps_D': params["ICU_discharge_rate"]}

    surge_specs = {'Hs': [(3, 7, 2), (8, 10, 5)],
                   'Hm': [(1, 10, 2), (5, 20, 1)],
                   'I': [(3, 4, 1)]}

    ts_results = transient_response_for_multi_surge_ex(surge_specs=surge_specs, times=times, fixed_params=params_formatted,
                                                    arrivals_mean=params['daily_ED_arrivals_avg'],
                                                    Ad_Hs_mean=params['stepdown_direct_admission_avg'],
                                                    Ad_Hm_mean=params['ward_direct_admission_avg'],
                                                    Ad_ICU_mean=params['ICU_direct_admission_avg'],
                                                    At_Hs_mean=params['stepdown_transfer_admission_avg'],
                                                    At_Hm_mean=params['ward_transfer_admission_avg'],
                                                    At_ICU_mean=params['ICU_transfer_admission_avg'])

    print('Baseline equilibrium:')
    print(f'WARD= {ts_results['x0'][1]}', f'\nSTEP= {ts_results['x0'][0]}', f'\nICU= {ts_results['x0'][2]}')

    print('Surge response results:')
    print(f'STEP= {ts_results['extra_beddays_per_comp']['Hs']}', f'\n WARD= {ts_results['extra_beddays_per_comp']['Hm']}', f'\nICU= {ts_results['extra_beddays_per_comp']['I']}')

    #print(ts_results['extra_beddays_per_comp']
    #ts_results['x0'])

    return results




if __name__ == "__main__":
    # Run example test when script is executed directly
    run_example_test()

# Baseline equilibrium:
#   WARD: 395.83
#   STEP: 9.37
#   ICU: 76.11
# Surge response results:
#   Total extra bed-days: 316.30
#   Extra bed-days by unit:
#     STEP: 22.78
#     WARD: 268.87
#     ICU: 24.65
