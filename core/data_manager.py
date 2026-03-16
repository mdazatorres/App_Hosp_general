import streamlit as st
import pandas as pd
from core.constants import DEFAULT_VALUES, BASE_DATA



def get_operational_inputs(required_data):
    st.sidebar.header("Hospital operational data")

    mode = st.sidebar.radio("Provide values:", ["Manual entry", "Upload Excel (daily data)"])
    values = {}

    # Define default values dictionary
    # ===============================
    # EXCEL UPLOAD
    # ===============================
    if mode == "Upload Excel (daily data)":
        file = st.sidebar.file_uploader("Upload Excel with daily time series", type=["xlsx", "xls"])

        if file:
            try:
                df = pd.read_excel(file)
                # Display first few rows to help user verify
                st.sidebar.write("Preview of uploaded data:")
                st.sidebar.dataframe(df.head(3))

                # Check which required columns are present
                available_cols = set(df.columns)
                missing_cols = set(required_data) - available_cols

                if missing_cols:
                    st.sidebar.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                    st.sidebar.info("Please ensure your Excel file contains all required columns.")

                    # Show which columns are available vs required
                    col1, col2 = st.sidebar.columns(2)
                    with col1:
                        st.write("✅ Available columns:")
                        for col in sorted(available_cols.intersection(required_data)):
                            st.write(f"  • {col}")
                    with col2:
                        st.write("❌ Missing columns:")
                        for col in sorted(missing_cols):
                            st.write(f"  • {col}")

                    # Option to use defaults for missing columns
                    if st.sidebar.button("Use defaults for missing columns"):
                        st.session_state['use_defaults_for_missing'] = True
                        st.rerun()
                else:
                    st.sidebar.success(f"✅ All {len(required_data)} required columns found!")

                    # Store the dataframe in session state for later use
                    st.session_state['uploaded_df'] = df
                    st.session_state['data_ready'] = True

                    # Show summary of available data
                    with st.sidebar.expander("📊 Data Summary"):
                        st.write(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
                        st.write(f"Total days: {len(df)}")

            except Exception as e:
                st.sidebar.error(f"Error loading file: {e}")

    # ===============================
    # MANUAL ENTRY WITH DEFAULTS
    # ===============================
    else:
        st.sidebar.markdown("### Enter planning values")

        # Create columns for better organization
        col1, col2 = st.sidebar.columns(2)

        for i, v in enumerate(sorted(required_data)):
            # Get default value from dictionary, or 0.0 if not found
            default_val = DEFAULT_VALUES.get(v, 0.0)

            if i % 2 == 0:
                with col1:
                    values[v] = st.number_input(v.replace('_', ' ').title(),min_value=0.0,
                        value=default_val, step=1.0, format="%.2f", key=f"input_{v}" )
            else:
                with col2:
                    values[v] = st.number_input(v.replace('_', ' ').title(), min_value=0.0,
                        value=default_val, step=1.0, format="%.2f", key=f"input_{v}")
        st.session_state['data_ready'] = True
        st.session_state['uploaded_df'] = None
    return values


def get_flows(selected_units):
    """Get active flows based on selected units"""
    from .constants import ALL_FLOWS
    return [(a, b) for a, b in ALL_FLOWS
            if a in selected_units and b in selected_units]


# =====================================================
# SELECT UNITS
# =====================================================
def get_selected_units():
    st.sidebar.header("Select hospital units")

    use_ed = st.sidebar.checkbox("Emergency Department", True)
    use_ward = st.sidebar.checkbox("General Ward (Med-Surg / Auxiliary)")
    use_icu = st.sidebar.checkbox("ICU")
    use_step = st.sidebar.checkbox("Step-down / PCU")

    units = []
    if use_ed:   units.append("ED")
    if use_ward: units.append("WARD")
    if use_icu:  units.append("ICU")
    if use_step: units.append("STEP")

    return units


def get_required_data(selected_units):
    """Get all required data variables based on selected units"""
    required_data = set()
    for u in selected_units:
        required_data.update(BASE_DATA.get(u, []))

    # Add conditional transfers
    transfers = [
        ("ED", "WARD", "ED_to_ward_admissions"),
        ("ED", "STEP", "ED_to_stepdown_admissions"),
        ("ED", "ICU", "ED_to_ICU_admissions")
    ]

    for a, b, name in transfers:
        if a in selected_units and b in selected_units:
            required_data.add(name)

    return required_data

