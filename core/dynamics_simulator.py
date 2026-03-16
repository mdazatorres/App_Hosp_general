import streamlit as st
import pandas as pd
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go
import plotly.express as px

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

            lambda_arr = float(params.get('daily_ED_arrivals_avg', 100))
            sigma = params.get('sigma', 2.0)
            omega = params.get('omega', 0.2)
            gamma = params.get('gamma', 1.0)

            dWdt = lambda_arr - (sigma + omega)*W
            dSdt = sigma * W - gamma*S

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
            if 'ED' in units:
                inflow_from_ED_to_step= params.get("xi_step",0)*B_step
            else:
                inflow_from_ED_to_step = 0
            inflow = (
                float(params.get("stepdown_direct_admission_avg",0)) +
                float(params.get("stepdown_transfer_admission_avg",0)) +
                inflow_from_ED_to_step )

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
            if "ED" in units:
                inflow_from_ED_to_ward= params.get("xi_ward",0)*B_ward
            else:
                inflow_from_ED_to_ward = 0

            inflow = (
                float(params.get("ward_direct_admission_avg",0)) +
                float(params.get("ward_transfer_admission_avg",0)) +
                inflow_from_ED_to_ward )

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
            if "ED" in units:
                inflow_from_ED_to_ICU = params.get("xi_ICU",0)*B_ICU
            else:
                inflow_from_ED_to_ICU = 0

            inflow = (float(params.get("ICU_direct_admission_avg",0)) +
                float(params.get("ICU_transfer_admission_avg",0)) +
                inflow_from_ED_to_ICU)

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
        fig.add_trace(go.Scatter( x=t, y=sol[:,i], mode='lines', name=label, line=dict(width=3,color=colors[i % len(colors)])))

    fig.update_layout(title="Hospital System Dynamics", xaxis_title="Days",
        yaxis_title="Patients", height=500, hovermode="x unified")

    st.plotly_chart(fig,use_container_width=True)

    final_values = {labels[i]:f"{sol[-1,i]:.1f}" for i in range(len(labels))}
    st.write("Final values after {} days".format(days))
    st.json(final_values)

