import streamlit as st
import pandas as pd
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go
import plotly.express as px


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

