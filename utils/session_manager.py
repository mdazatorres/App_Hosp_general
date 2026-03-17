# core/session_manager.py
import streamlit as st
from typing import Any, Dict, Optional

def initialize_session():
    """Initialize all session state variables"""
    defaults = {
        'scenarios': {},
        'current_params': {},
        'data_ready': False,
        'uploaded_df': None,
        'uploaded_df_for_plot': None  # Add this line
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_session_value(key: str, default: Any = None) -> Any:
    """Get a value from session state"""
    return st.session_state.get(key, default)

def set_session_value(key: str, value: Any):
    """Set a value in session state"""
    st.session_state[key] = value

def update_current_params(params: Dict):
    """Update current parameters in session"""
    st.session_state['current_params'] = paramsloaded_df = None


# helpers.py contents in case some error shows up

# def safe_get_value(values, key, default, warning_msg=None):
#     """Safely get a value from dict, with default and optional warning"""
#     val = values.get(key)
#     if val is None:
#         if warning_msg:
#             st.sidebar.warning(warning_msg)
#         return default
#     return float(val)
#
# def initialize_session_state():
#     """Initialize all session state variables"""
#     if 'scenarios' not in st.session_state:
#         st.session_state.scenarios = {}
#     if 'current_params' not in st.session_state:
#         st.session_state.current_params = {}
#     if 'data_ready' not in st.session_state:
#         st.session_state.data_ready = False
#     if 'uploaded_df' not in st.session_state:
#         st.session_state.uploaded_df = None
