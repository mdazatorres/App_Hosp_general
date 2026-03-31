# core/data_processor.py
import streamlit as st
from typing import Dict, Tuple
import pandas as pd
from core.constants import DEFAULT_VALUES
from core.parameter_calculator import compute_parameters_from_entry, compute_parameters_from_excel


def process_input_data(required_data: set, selected_units: list, mode: str) -> Tuple[Dict, Dict]:
    """
    Process input data based on mode (upload, manual, or default)
    Returns (values, params)
    """
    from core.data_manager import get_operational_inputs

    # Get operational inputs
    values = get_operational_inputs(required_data, selected_units, mode)

    # Check if we have uploaded data
    if st.session_state.get('data_ready', False) and st.session_state.get('uploaded_df') is not None:
        return _process_uploaded_data(st.session_state['uploaded_df'], selected_units)

    # Check if we have manual entry values
    elif values and any(v != 0 for v in values.values()):
        return _process_manual_data(values, selected_units)

    # Default mode
    else:
        return _process_default_data(selected_units)


def _process_uploaded_data(df: pd.DataFrame, selected_units: list) -> Tuple[Dict, Dict]:
    """Process uploaded Excel data"""
    params = compute_parameters_from_excel(df, selected_units)
    st.success("✅ Parameters computed successfully from uploaded data!")
    values = DEFAULT_VALUES.copy()  # For display only
    return values, params


def _process_manual_data(values: Dict, selected_units: list) -> Tuple[Dict, Dict]:
    """Process manually entered data"""
    params = compute_parameters_from_entry(values, selected_units)
    st.info("📝 Using manually entered values")
    return values, params


def _process_default_data(selected_units: list) -> Tuple[Dict, Dict]:
    """Use default values"""
    st.sidebar.info("ℹ️ Using default values. Upload Excel or use Manual entry to customize.")
    values = DEFAULT_VALUES.copy()
    params = compute_parameters_from_entry(values, selected_units)
    st.session_state['data_ready'] = True
    st.session_state['uploaded_df'] = None
    return values, params