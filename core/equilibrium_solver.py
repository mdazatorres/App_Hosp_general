import streamlit as st
import pandas as pd
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go
import plotly.express as px



# =====================================================
# SOLVE EQUILIBRIUM
# =====================================================
def solve_equilibrium(units, params, values):
    """
    Solve steady-state bed occupancy by linear flow balance.
    """

    st.subheader("⚖️ Equilibrium Analysis")

    equilibrium = {}

    if not params or not values:
        st.warning("Missing parameters or input values.")
        return {}

    # =====================================================
    # ED EQUILIBRIUM
    # =====================================================
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

    # =====================================================
    # BOARDING EQUILIBRIUM (closed-form)
    # =====================================================
    if "ED" in units:

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

    # =====================================================
    # INPATIENT LINEAR SYSTEM
    # =====================================================
    inpatient_units = [u for u in ["STEP", "WARD", "ICU"] if u in units]

    if len(inpatient_units) > 0:

        n = len(inpatient_units)
        A = np.zeros((n, n))
        b = np.zeros(n)

        unit_index = {u: i for i, u in enumerate(inpatient_units)}

        for u in inpatient_units:

            i = unit_index[u]

            if u == "STEP":
                direct = float(params.get("stepdown_direct_admission_avg", 0))
                transfer = float(params.get("stepdown_transfer_admission_avg", 0))
                if 'ED' in units:
                    boarding = params['xi_step'] * B_step
                else:
                    boarding = 0
                mu = params.get("step_discharge_rate", 0)

                A[i, i] += mu
                b[i] = direct + transfer + boarding

                if "ICU" in inpatient_units:
                    j = unit_index["ICU"]
                    rho = params.get("ICU_to_step_rate", 0)
                    A[i, j] -= rho
                    A[j, j] += rho


            # ---------- External inflow ----------
            if u == "WARD":
                direct = float(params.get("ward_direct_admission_avg", 0))
                transfer = float(params.get("ward_transfer_admission_avg", 0))
                if 'ED' in units:
                    boarding = params['xi_ward'] * B_ward
                else:
                    boarding = 0
                mu = params.get("ward_discharge_rate", 0)

                A[i, i] += mu
                b[i] = direct + transfer + boarding

                # From ICU
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
                direct = float(params.get("ICU_direct_admission_avg", 0))
                transfer = float(params.get("ICU_transfer_admission_avg", 0))
                if 'ED' in units:
                    boarding = params['xi_ICU'] * B_ICU
                else:
                    boarding = 0
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

    # =====================================================
    # DISPLAY RESULTS
    # =====================================================
    if equilibrium:

        eq_df = pd.DataFrame([
            {"Compartment": k,
             "Equilibrium Occupancy": f"{v:.1f} patients",
             "Value": v}
            for k, v in equilibrium.items()
        ])

        col1, col2 = st.columns([2, 1])

        with col1:
            st.dataframe(eq_df, use_container_width=True)

        with col2:
            fig = go.Figure()
            fig.add_bar(
                x=list(equilibrium.keys()),
                y=list(equilibrium.values())
            )
            fig.update_layout(
                title="Equilibrium Occupancy",
                yaxis_title="Patients",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        total = sum(equilibrium.values())
        st.metric("Total Patients in System", f"{total:.1f}")

    else:
        st.info("Not enough data to compute equilibrium.")

    return equilibrium


