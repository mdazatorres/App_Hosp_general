# flake8: noqa
# pylint: disable=undefined-variable
#import streamlit as st # pylint: disable=import-error
from typing import List, Dict
import streamlit as st
import pandas as pd
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go
import plotly.express as px
# =====================================================
# COMPUTE PARAMETERS FROM DATA
# =====================================================


def compute_parameters_from_entry(values, selected_units):
    # Force usage at the very beginning
    MIN2DAY = 1.0 / 1440.0


    params = {}
    # if not values:
    #     st.warning("No input values provided.")
    if selected_units is None:
        selected_units = []
    # ===== ED PARAMETERS =====
    # noinspection PyUnresolvedReferences
    if "ED" in selected_units: # PyCharm specific
        # Get ED values with defaults
        # Wait time in minutes → sigma
        mean_wait_min = float(values.get('avg_ED_wait_time'))
        mean_wait = max(mean_wait_min * MIN2DAY, 1e-6)
        params["sigma"] = 1.0 / max(mean_wait, 1e-6)

        mean_treatment_min = float(values.get('avg_ED_treatment_time_min', 159.0))  # 2.65 hours = 159 min
        mean_treatment = max(mean_treatment_min * MIN2DAY, 1e-6)
        params["gamma"] = 1.0 / max(mean_treatment, 1e-6)

        # Treatment time in minutes → gamma
        mean_board_min = float(values.get('avg_ED_boarding_time'))
        mean_board= max(mean_board_min * MIN2DAY, 1e-6)

        params["xi_ward"] = 1.0 / max(mean_board, 1e-6)
        params["xi_step"] = 1.0 / max(mean_board, 1e-6)
        params["xi_ICU"] = 1.0 / max(mean_board, 1e-6)

        #mean_board_days = max(mean_board_min * MIN2DAY, 1e-6)

        total_arr = float(values.get('daily_ED_arrivals'))
        total_lwbs = float(values.get('left_without_being_seen'))
        total_adm_from_ED = float(values.get('total_adm_from_ED'))

        #MIN2DAY = 1.0 / 1440.0, check this

        # Wait time to treatment rate

        params['daily_ED_arrivals_avg']= total_arr

        # Left without being seen calculation
        if total_arr > 0:
            f_lwbs = min(total_lwbs / total_arr, 0.99)  # Cap at 0.99
            params["omega"] = params["sigma"] * f_lwbs / max((1.0 - f_lwbs), 1e-9)
        else:
            params["omega"] = 0.1

        # Admission probabilities
        seen_total = max(total_arr - total_lwbs, 1e-6)


        ##########################
        if "WARD" in selected_units:
            ed_to_ward = float(values.get('ED_to_ward_admissions')) # check
            params["pED_to_ward"] = min(ed_to_ward / seen_total, 1.0)
        if "STEP" in selected_units:
            ed_to_step = float(values.get('ED_to_stepdown_admissions', total_arr * 0.1))
            params["pED_to_step"] = min(ed_to_step / seen_total, 1.0)
        if "ICU" in selected_units:
            ed_to_icu = float(values.get('ED_to_ICU_admissions', total_arr * 0.05))
            params["pED_to_ICU"] = min(ed_to_icu / seen_total, 1.0)

    # ===== WARD PARAMETERS =====
    if "WARD" in selected_units:

        ward_beds = float(values.get('ward_occupied_beds', 50))
        ward_beds = max(ward_beds, 1)
        # varphi
        params["ward_discharge_rate"] = float(values.get('ward_discharges')) / ward_beds
        params["ward_to_ICU_rate"] = float(values.get('ward_to_ICU')) / ward_beds
        params["ward_direct_admission_avg"]= values.get("ward_direct_admission")
        params["ward_transfer_admission_avg"] = values.get("ward_transfer_admission")


    # ===== STEP-DOWN PARAMETERS =====
    if "STEP" in selected_units:
        #psi
        step_beds = float(values.get('stepdown_occupied_beds', 10))
        step_beds = max(step_beds, 1)
        # varphi
        params["step_discharge_rate"] = float(values.get('stepdown_discharges', 12)) / step_beds
        params["step_to_ICU_rate"] = float(values.get("stepdown_to_ICU", 1)) / step_beds
        params["step_to_ward_rate"] = float(values.get("stepdown_to_ward", 1)) / step_beds
        params["stepdown_direct_admission_avg"] = values.get("stepdown_direct_admission")
        params["stepdown_transfer_admission_avg"] = values.get("stepdown_transfer_admission")



    # ===== ICU PARAMETERS =====
    if "ICU" in selected_units:
        icu_beds = float(values.get('ICU_occupied_beds', 20))
        icu_beds = max(icu_beds, 1)

        params["ICU_discharge_rate"] = float(values.get('ICU_discharges', 6)) / icu_beds
        params["ICU_to_ward_rate"] = float(values.get('ICU_to_ward', 3)) / icu_beds
        params["ICU_to_step_rate"] = float(values.get('ICU_to_stepdown', 3)) / icu_beds
        params["ICU_direct_admission_avg"] = values.get("ICU_direct_admission")
        params["ICU_transfer_admission_avg"] = values.get("ICU_transfer_admission")

        #params["ICU_to_ward_rate"] = float(values.get('ICU_transf', 3)) / icu_beds
        #params["ICU_to_step_rate"] = params["ICU_to_ward_rate"] * 0.3  # Estimate

    return params



# def compute_parameters_from_entry_old(values, selected_units):
#     # Force usage at the very beginning
#     MIN2DAY = 1.0 / 1440.0
#
#     params = {}
#     # if not values:
#     #     st.warning("No input values provided.")
#     if selected_units is None:
#         selected_units = []
#     # ===== ED PARAMETERS =====
#     # noinspection PyUnresolvedReferences
#     if "ED" in selected_units: # PyCharm specific
#         # Get ED values with defaults
#         mean_LOS_min = float(values.get('avg_ED_length_of_stay'))
#         mean_wait_min = float(values.get('avg_ED_wait_time'))
#         mean_board_min = float(values.get('avg_ED_boarding_time'))
#         mean_LOS= max(mean_LOS_min * MIN2DAY, 1e-6)
#         mean_wait = max(mean_wait_min * MIN2DAY, 1e-6)
#         mean_board= max(mean_board_min * MIN2DAY, 1e-6)
#
#         #mean_board_days = max(mean_board_min * MIN2DAY, 1e-6)
#
#         total_arr = float(values.get('daily_ED_arrivals'))
#         total_lwbs = float(values.get('left_without_being_seen'))
#         total_adm_from_ED = float(values.get('total_adm_from_ED'))
#
#         #MIN2DAY = 1.0 / 1440.0, check this
#
#         # Wait time to treatment rate
#         params["sigma"] = 1.0 / max(mean_wait, 1e-6)
#         params['daily_ED_arrivals_avg']= total_arr
#
#         # Left without being seen calculation
#         if total_arr > 0:
#             f_lwbs = min(total_lwbs / total_arr, 0.99)  # Cap at 0.99
#             params["omega"] = params["sigma"] * f_lwbs / max((1.0 - f_lwbs), 1e-9)
#         else:
#             params["omega"] = 0.1
#
#         # Admission probabilities
#         seen_total = max(total_arr - total_lwbs, 1e-6)
#
#         if seen_total <= 0:
#             p_admit = 0.15  # fallback
#         else:
#             p_admit = total_adm_from_ED / seen_total
#
#         # Treatment rate (service time)
#         mean_service = max(mean_LOS - mean_wait - p_admit*mean_board,1e-6)
#         params["gamma"] = 1.0 / mean_service
#
#         # Boarding rates
#         params["xi_ward"] = 1.0 / max(mean_board, 1e-6) # check this ! what happens in the equilibrium
#         params["xi_step"] = 1.0 / max(mean_board, 1e-6)
#         params["xi_ICU"] = 1.0 / max(mean_board, 1e-6)
#
#
#         ##########################
#         if "WARD" in selected_units:
#             ed_to_ward = float(values.get('ED_to_ward_admissions')) # check
#             params["pED_to_ward"] = min(ed_to_ward / seen_total, 1.0)
#         if "STEP" in selected_units:
#             ed_to_step = float(values.get('ED_to_stepdown_admissions', total_arr * 0.1))
#             params["pED_to_step"] = min(ed_to_step / seen_total, 1.0)
#         if "ICU" in selected_units:
#             ed_to_icu = float(values.get('ED_to_ICU_admissions', total_arr * 0.05))
#             params["pED_to_ICU"] = min(ed_to_icu / seen_total, 1.0)
#
#     # ===== WARD PARAMETERS =====
#     if "WARD" in selected_units:
#
#         ward_beds = float(values.get('ward_occupied_beds', 50))
#         ward_beds = max(ward_beds, 1)
#         # varphi
#         params["ward_discharge_rate"] = float(values.get('ward_discharges')) / ward_beds
#         params["ward_to_ICU_rate"] = float(values.get('ward_to_ICU')) / ward_beds
#         params["ward_direct_admission_avg"]= values.get("ward_direct_admission")
#         params["ward_transfer_admission_avg"] = values.get("ward_transfer_admission")
#
#
#     # ===== STEP-DOWN PARAMETERS =====
#     if "STEP" in selected_units:
#         #psi
#         step_beds = float(values.get('stepdown_occupied_beds', 10))
#         step_beds = max(step_beds, 1)
#         # varphi
#         params["step_discharge_rate"] = float(values.get('stepdown_discharges', 12)) / step_beds
#         params["step_to_ICU_rate"] = float(values.get("stepdown_to_ICU", 1)) / step_beds
#         params["step_to_ward_rate"] = float(values.get("stepdown_to_ward", 1)) / step_beds
#         params["stepdown_direct_admission_avg"] = values.get("stepdown_direct_admission")
#         params["stepdown_transfer_admission_avg"] = values.get("stepdown_transfer_admission")
#
#
#
#     # ===== ICU PARAMETERS =====
#     if "ICU" in selected_units:
#         icu_beds = float(values.get('ICU_occupied_beds', 20))
#         icu_beds = max(icu_beds, 1)
#
#         params["ICU_discharge_rate"] = float(values.get('ICU_discharges', 6)) / icu_beds
#         params["ICU_to_ward_rate"] = float(values.get('ICU_to_ward', 3)) / icu_beds
#         params["ICU_to_step_rate"] = float(values.get('ICU_to_stepdown', 3)) / icu_beds
#         params["ICU_direct_admission_avg"] = values.get("ICU_direct_admission")
#         params["ICU_transfer_admission_avg"] = values.get("ICU_transfer_admission")
#
#         #params["ICU_to_ward_rate"] = float(values.get('ICU_transf', 3)) / icu_beds
#         #params["ICU_to_step_rate"] = params["ICU_to_ward_rate"] * 0.3  # Estimate
#
#     return params

def compute_parameters_from_excel(df, selected_units):
    """
    Compute model parameters directly from daily time series data
    Similar to your original compute_params_from_df function
    """
    params = {}
    MIN2DAY = 1.0 / 1440.0
    # ===== ED PARAMETERS =====
    if "ED" in selected_units:
        # Calculate mean waiting time in days
        if 'avg_ED_wait_time' in df.columns:
            mean_wait_min = float(df['avg_ED_wait_time'].dropna().mean())
            mean_wait_days = max(mean_wait_min * MIN2DAY, 1e-6)
        else:
            mean_wait_days = 0.078  # default

        # Calculate mean boarding time in days
        if 'avg_ED_boarding_time' in df.columns:
            mean_board_min = float(df['avg_ED_boarding_time'].dropna().mean())
            mean_board_days = max(mean_board_min * MIN2DAY, 1e-6)
        else:
            mean_board_days = 0.676  # default

        # Calculate mean LOS in days
        if 'avg_ED_length_of_stay' in df.columns:
            mean_LOS_min = float(df['avg_ED_length_of_stay'].dropna().mean())
            mean_LOS_days = max(mean_LOS_min * MIN2DAY, 1e-6)
        else:
            mean_LOS_days = 0.316  # default

        # Wait time to treatment rate
        params["sigma"] = 1.0 / max(mean_wait_days, 1e-6)

        # Left without being seen calculation
        if 'daily_ED_arrivals' in df.columns and 'left_without_being_seen' in df.columns:
            total_arr = float(df['daily_ED_arrivals'].sum())
            total_lwbs = float(df['left_without_being_seen'].sum())
            params['daily_ED_arrivals_avg'] = float(df['daily_ED_arrivals'].mean())

            if total_arr > 0:
                f_lwbs = min(total_lwbs / total_arr, 0.99)
                params["omega"] = params["sigma"] * f_lwbs / max((1.0 - f_lwbs), 1e-9)
            else:
                params["omega"] = 0.1
        else:
            params["omega"] = 0.1

        # Admission probabilities
        if 'daily_ED_arrivals' in df.columns and 'left_without_being_seen' in df.columns:
            seen_total = max(total_arr - total_lwbs, 1e-6)
        else:
            seen_total = 100  # fallback

        # Total admissions from ED
        if 'total_adm_from_ED' in df.columns:
            total_adm_from_ED = float(df['total_adm_from_ED'].sum())
        else:
            # Try to sum individual admission columns if available
            admit_cols = []
            if 'ED_to_ward_admissions' in df.columns:
                admit_cols.append('ED_to_ward_admissions')
            if 'ED_to_stepdown_admissions' in df.columns:
                admit_cols.append('ED_to_stepdown_admissions')
            if 'ED_to_ICU_admissions' in df.columns:
                admit_cols.append('ED_to_ICU_admissions')

            if admit_cols:
                total_adm_from_ED = float(df[admit_cols].sum().sum())
            else:
                total_adm_from_ED = 50.02  # default

        if seen_total <= 0:
            p_admit = 0.15
        else:
            p_admit = total_adm_from_ED / seen_total

        # Treatment rate (service time)
        mean_service = max(mean_LOS_days - mean_wait_days - p_admit * mean_board_days, 1e-6)
        params["gamma"] = 1.0 / mean_service

        # Boarding rates
        params["xi_ward"] = 1.0 / max(mean_board_days, 1e-6)
        params["xi_step"] = 1.0 / max(mean_board_days, 1e-6)
        params["xi_ICU"] = 1.0 / max(mean_board_days, 1e-6)

        # ED to unit admission probabilities
        if "WARD" in selected_units and 'ED_to_ward_admissions' in df.columns:
            ed_to_ward = float(df['ED_to_ward_admissions'].sum())
            params["pED_to_ward"] = min(ed_to_ward / seen_total, 1.0)
        else:
            params["pED_to_ward"] = 0.3

        if "STEP" in selected_units and 'ED_to_stepdown_admissions' in df.columns:
            ed_to_step = float(df['ED_to_stepdown_admissions'].sum())
            params["pED_to_step"] = min(ed_to_step / seen_total, 1.0)
        else:
            params["pED_to_step"] = 0.1

        if "ICU" in selected_units and 'ED_to_ICU_admissions' in df.columns:
            ed_to_icu = float(df['ED_to_ICU_admissions'].sum())
            params["pED_to_ICU"] = min(ed_to_icu / seen_total, 1.0)
        else:
            params["pED_to_ICU"] = 0.05

    # ===== WARD PARAMETERS =====
    if "WARD" in selected_units:
        if 'ward_occupied_beds' in df.columns:
            ward_beds = float(df['ward_occupied_beds'].sum())
            ward_beds = max(ward_beds, 1)
        else:
            ward_beds = 400.33

        # Ward discharge rate
        if 'ward_discharges' in df.columns:
            params["ward_discharge_rate"] = float(df['ward_discharges'].sum()) / ward_beds
        else:
            params["ward_discharge_rate"] = 66.37 / ward_beds

        # Ward to ICU rate
        if 'ward_to_ICU' in df.columns:
            params["ward_to_ICU_rate"] = float(df['ward_to_ICU'].sum()) / ward_beds
        else:
            params["ward_to_ICU_rate"] = 2.98 / ward_beds

        # Direct and transfer admissions
        if 'ward_direct_admission' in df.columns:
            params["ward_direct_admission_avg"] = float(df['ward_direct_admission'].mean())
        else:
            params["ward_direct_admission_avg"] = 9.27

        if 'ward_transfer_admission' in df.columns:
            params["ward_transfer_admission_avg"] = float(df['ward_transfer_admission'].mean())
        else:
            params["ward_transfer_admission_avg"] = 7.63

    # ===== STEP-DOWN PARAMETERS =====
    if "STEP" in selected_units:
        if 'stepdown_occupied_beds' in df.columns:
            step_beds = float(df['stepdown_occupied_beds'].sum())
            step_beds = max(step_beds, 1)
        else:
            step_beds = 8.39

        # Step-down discharge rate
        if 'stepdown_discharges' in df.columns:
            params["step_discharge_rate"] = float(df['stepdown_discharges'].sum()) / step_beds
        else:
            params["step_discharge_rate"] = 2.33 / step_beds

        # Step-down to ICU rate
        if 'stepdown_to_ICU' in df.columns:
            params["step_to_ICU_rate"] = float(df['stepdown_to_ICU'].sum()) / step_beds
        else:
            params["step_to_ICU_rate"] = 0.78 / step_beds

        # Step-down to Ward rate
        if 'stepdown_to_ward' in df.columns:
            # comment this line is just for the synthetic example, and uncommented the line below
            params["step_to_ward_rate"] = float(df['stepdown_to_ward'].mean()) / float(df['stepdown_occupied_beds'].mean())
            #params["step_to_ward_rate"] = float(df['stepdown_to_ward'].sum()) / step_beds
        else:
            params["step_to_ward_rate"] = 3.52 / step_beds

        # Direct and transfer admissions
        if 'stepdown_direct_admission' in df.columns:
            params["stepdown_direct_admission_avg"] = float(df['stepdown_direct_admission'].mean())
        else:
            params["stepdown_direct_admission_avg"] = 5.28

        if 'stepdown_transfer_admission' in df.columns:
            params["stepdown_transfer_admission_avg"] = float(df['stepdown_transfer_admission'].mean())
        else:
            params["stepdown_transfer_admission_avg"] = 0.59

    # ===== ICU PARAMETERS =====
    if "ICU" in selected_units:
        if 'ICU_occupied_beds' in df.columns:
            icu_beds = float(df['ICU_occupied_beds'].sum())
            icu_beds = max(icu_beds, 1)
        else:
            icu_beds = 76.94

        # ICU discharge rate
        if 'ICU_discharges' in df.columns:
            params["ICU_discharge_rate"] = float(df['ICU_discharges'].sum()) / icu_beds
        else:
            params["ICU_discharge_rate"] = 3.05 / icu_beds

        # ICU to Ward rate
        if 'ICU_to_ward' in df.columns:
            params["ICU_to_ward_rate"] = float(df['ICU_to_ward'].sum()) / icu_beds
        else:
            params["ICU_to_ward_rate"] = 12.80 / icu_beds

        # ICU to Step-down rate
        if 'ICU_to_stepdown' in df.columns:
            params["ICU_to_step_rate"] = float(df['ICU_to_stepdown'].sum()) / icu_beds
        else:
            params["ICU_to_step_rate"] = 0.1 / icu_beds

        # Direct and transfer admissions
        if 'ICU_direct_admission' in df.columns:
            #params["ICU_direct_admission_avg"] = float(df['ICU_direct_admission'].mean())
            params["ICU_direct_admission_avg"] = df.loc[df['ICU_direct_admission'] != 0, 'ICU_direct_admission'].median()
        else:
            params["ICU_direct_admission_avg"] = 2.09

        if 'ICU_transfer_admission' in df.columns:
            params["ICU_transfer_admission_avg"] = float(df['ICU_transfer_admission'].mean())
        else:
            params["ICU_transfer_admission_avg"] = 3.37

    return params