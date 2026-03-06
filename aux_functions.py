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

        lambda_arr = float(values.get("daily_ED_arrivals", 100))
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
                direct = float(values.get("stepdown_direct_admission", 0))
                transfer = float(values.get("stepdown_transfer_admission", 0))
                boarding = params['xi_step'] * B_step
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
                direct = float(values.get("ward_direct_admission", 0))
                transfer = float(values.get("ward_transfer_admission", 0))
                boarding = params['xi_ward'] * B_ward
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
                direct = float(values.get("ICU_direct_admission", 0))
                transfer = float(values.get("ICU_transfer_admission", 0))
                boarding = params['xi_ICU'] * B_ICU
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


# =====================================================
# TIME DYNAMICS SIMULATION
# =====================================================
def simulate_dynamics1(units, params, values, days=30):
    """
    Simulate the system dynamics over time
    """
    st.subheader("📈 Time Dynamics Simulation")

    # Define the ODE system based on selected units
    def ode_system(y, t):
        dydt = []
        idx = 0

        if "ED" in units:
            # W and S for ED
            W, S = y[idx], y[idx + 1]
            lambda_arr = float(values.get('daily_ED_arrivals', 100))
            sigma = params.get('sigma', 2.0)
            omega = params.get('omega', 0.2)
            gamma = params.get('gamma', 1.0)

            dWdt = lambda_arr - (sigma + omega) * W
            dSdt = sigma * W - gamma * S

            dydt.extend([dWdt, dSdt])
            idx += 2

            # Boarding areas
            if "WARD" in units and "xi_ward" in params:
                B_ward = y[idx]
                dB_warddt = params.get('pED_to_ward', 0.3) * gamma * S - params['xi_ward'] * B_ward
                dydt.append(dB_warddt)
                idx += 1

            if "STEP" in units and "xi_step" in params:
                B_step = y[idx]
                dB_stepdt = params.get('pED_to_step', 0.1) * gamma * S - params['xi_step'] * B_step
                dydt.append(dB_stepdt)
                idx += 1

            if "ICU" in units and "xi_ICU" in params:
                B_icu = y[idx]
                dB_icudt = params.get('pED_to_ICU', 0.05) * gamma * S - params['xi_ICU'] * B_icu
                dydt.append(dB_icudt)
                idx += 1

        # Add other unit equations here as needed

        return dydt

    # Set up initial conditions
    y0 = []
    labels = []

    if "ED" in units:
        y0.extend([50, 20])  # Initial W and S
        labels.extend(['Waiting', 'Treatment'])

        if "WARD" in units:
            y0.append(30)
            labels.append('Ward Boarding')
        if "STEP" in units:
            y0.append(15)
            labels.append('Step Boarding')
        if "ICU" in units:
            y0.append(10)
            labels.append('ICU Boarding')

    # Time points
    t = np.linspace(0, days, days * 10)

    # Solve ODE
    try:
        sol = odeint(ode_system, y0, t)

        # Plot results
        fig = go.Figure()

        colors = px.colors.qualitative.Set1
        for i, label in enumerate(labels):
            fig.add_trace(go.Scatter(x=t, y=sol[:, i],
                                     mode='lines',
                                     name=label,
                                     line=dict(color=colors[i % len(colors)], width=2)))

        fig.update_layout(title="System Dynamics Over Time",
                          xaxis_title="Days",
                          yaxis_title="Number of Patients",
                          hovermode='x unified',
                          height=500)

        st.plotly_chart(fig, use_container_width=True)

        # Show final values
        final_values = {labels[i]: f"{sol[-1, i]:.1f}" for i in range(len(labels))}
        st.write("**Final values after {} days:**".format(days))
        st.json(final_values)

    except Exception as e:
        st.error(f"Error in simulation: {e}")
        st.info("Try adjusting parameters or providing more complete data.")


def simulate_dynamics(units, params, values, days=30):
    """
    Simulate the system dynamics over time
    """
    st.subheader("📈 Time Dynamics Simulation")

    def ode_system(y, t):

        dydt = []
        idx = 0

        # ---------------- ED ----------------
        if "ED" in units:

            W, S = y[idx], y[idx+1]
            idx += 2

            lambda_arr = float(values.get('daily_ED_arrivals', 100))
            sigma = params.get('sigma', 2.0)
            omega = params.get('omega', 0.2)
            gamma = params.get('gamma', 1.0)

            dWdt = lambda_arr - (sigma + omega)*W
            dSdt = sigma*W - gamma*S

            dydt.extend([dWdt, dSdt])

            # Boarding variables
            if "WARD" in units:
                B_ward = y[idx]
                dB_ward = params.get('pED_to_ward',0.3)*gamma*S - params.get('xi_ward',0)*B_ward
                dydt.append(dB_ward)
                idx += 1
            else:
                B_ward = 0

            if "STEP" in units:
                B_step = y[idx]
                dB_step = params.get('pED_to_step',0.1)*gamma*S - params.get('xi_step',0)*B_step
                dydt.append(dB_step)
                idx += 1
            else:
                B_step = 0

            if "ICU" in units:
                B_ICU = y[idx]
                dB_ICU = params.get('pED_to_ICU',0.05)*gamma*S - params.get('xi_ICU',0)*B_ICU
                dydt.append(dB_ICU)
                idx += 1
            else:
                B_ICU = 0

        # ---------------- STEP ----------------
        if "STEP" in units:

            STEP = y[idx]
            idx += 1

            inflow = (
                float(values.get("stepdown_direct_admission",0)) +
                float(values.get("stepdown_transfer_admission",0)) +
                params.get("xi_step",0)*B_step
            )

            if "ICU" in units:
                ICU = y[labels.index("ICU")]
                inflow += params.get("ICU_to_step_rate",0)*ICU

            outflow = params.get("step_discharge_rate",0)*STEP

            if "ICU" in units:
                outflow += params.get("step_to_ICU_rate",0)*STEP

            if "WARD" in units:
                outflow += params.get("step_to_ward_rate",0)*STEP

            dSTEP = inflow - outflow
            dydt.append(dSTEP)

        # ---------------- WARD ----------------
        if "WARD" in units:

            WARD = y[idx]
            idx += 1

            inflow = (
                float(values.get("ward_direct_admission",0)) +
                float(values.get("ward_transfer_admission",0)) +
                params.get("xi_ward",0)*B_ward
            )

            if "ICU" in units:
                ICU = y[labels.index("ICU")]
                inflow += params.get("ICU_to_ward_rate",0)*ICU

            if "STEP" in units:
                STEP = y[labels.index("STEP")]
                inflow += params.get("step_to_ward_rate",0)*STEP

            outflow = params.get("ward_discharge_rate",0)*WARD

            if "ICU" in units:
                outflow += params.get("ward_to_ICU_rate",0)*WARD

            dWARD = inflow - outflow
            dydt.append(dWARD)

        # ---------------- ICU ----------------
        if "ICU" in units:

            ICU = y[idx]
            idx += 1

            inflow = (
                float(values.get("ICU_direct_admission",0)) +
                float(values.get("ICU_transfer_admission",0)) +
                params.get("xi_ICU",0)*B_ICU
            )

            if "WARD" in units:
                WARD = y[labels.index("WARD")]
                inflow += params.get("ward_to_ICU_rate",0)*WARD

            if "STEP" in units:
                STEP = y[labels.index("STEP")]
                inflow += params.get("step_to_ICU_rate",0)*STEP

            outflow = params.get("ICU_discharge_rate",0)*ICU

            if "WARD" in units:
                outflow += params.get("ICU_to_ward_rate",0)*ICU

            if "STEP" in units:
                outflow += params.get("ICU_to_step_rate",0)*ICU

            dICU = inflow - outflow
            dydt.append(dICU)

        return dydt


    # ---------------- INITIAL CONDITIONS ----------------

    y0 = []
    labels = []

    if "ED" in units:
        y0 += [10,10]
        labels += ["Waiting","Treatment"]

        if "WARD" in units:
            y0.append(5)
            labels.append("Ward Boarding")

        if "STEP" in units:
            y0.append(5)
            labels.append("Step Boarding")

        if "ICU" in units:
            y0.append(2)
            labels.append("ICU Boarding")

    if "STEP" in units:
        y0.append(9.0)
        labels.append("STEP")

    if "WARD" in units:
        y0.append(436)
        labels.append("WARD")

    if "ICU" in units:
        y0.append(72)
        labels.append("ICU")


    # ---------------- SOLVE ----------------

    t = np.linspace(0, days, days*10)

    sol = odeint(ode_system, y0, t)

    # ---------------- PLOT ----------------

    fig = go.Figure()

    colors = px.colors.qualitative.Set1

    for i,label in enumerate(labels):

        fig.add_trace(
            go.Scatter(
                x=t,
                y=sol[:,i],
                mode='lines',
                name=label,
                line=dict(width=3,color=colors[i % len(colors)])
            )
        )

    fig.update_layout(
        title="Hospital System Dynamics",
        xaxis_title="Days",
        yaxis_title="Patients",
        height=500,
        hovermode="x unified"
    )

    st.plotly_chart(fig,use_container_width=True)

    final_values = {labels[i]:f"{sol[-1,i]:.1f}" for i in range(len(labels))}
    st.write("Final values after {} days".format(days))
    st.json(final_values)
