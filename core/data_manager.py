import streamlit as st
import pandas as pd
from core.constants import DEFAULT_VALUES, BASE_DATA, BASE_DATA_MANUAL,DATA_DICTIONARY

def download_excel_template(required_data):
    with st.sidebar.expander("📥 Need a template?", expanded=False):
        st.markdown("Download a template with the required columns:")

        # Create template dataframe with required columns
        template_df = pd.DataFrame(columns=sorted(required_data))

        # Add a sample row with default values (optional)
        sample_row = {col: DEFAULT_VALUES.get(col, 0) for col in sorted(required_data)}
        template_df.loc[0] = sample_row

        # Add a 'Date' column if not already present
        if 'Date' not in template_df.columns:
            template_df.insert(0, 'Date', pd.date_range(start='2024-01-01', periods=1))

        # Create Excel file in memory
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            template_df.to_excel(writer, sheet_name='Data Template', index=False)

            # Add a second sheet with instructions
            instructions = pd.DataFrame({
                'Instruction': [
                    '1. Replace the sample data with your actual data',
                    '2. Add rows for each day (one row per date)',
                    '3. Ensure all columns have the correct units',
                    '4. Save the file and upload it below'
                ]
            })
            instructions.to_excel(writer, sheet_name='Instructions', index=False)

        output.seek(0)

        st.download_button(
            label="📊 Download Excel Template",
            data=output,
            file_name="hospital_data_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

        st.caption(f"Template includes {len(required_data)} required columns + Date column")

    #st.sidebar.markdown("---")

def get_operational_inputs(required_data,selected_units, mode):

    values = {}

    # Define default values dictionary
    # ===============================
    # EXCEL UPLOAD
    # ===============================
    if mode == "Upload Excel (daily data)":
        st.sidebar.info("📋 Required columns are listed in the **Model Summary** tab. Download the template below for a ready-to-use format.")
        download_excel_template(required_data)
        file = st.sidebar.file_uploader("Upload Excel with daily time series", type=["xlsx", "xls"])
        missing_defaults_used = []

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
                    st.sidebar.write("**Default values will be used for:**")
                    for col in sorted(missing_cols):
                        default_val = DEFAULT_VALUES.get(col, 0.0)
                        st.sidebar.write(f"  • {col} (default: {default_val:.2f})")
                        missing_defaults_used.append((col, default_val))

                    # Option to use defaults for missing columns
                        # Option to proceed or cancel
                    col_btn1, col_btn2 = st.sidebar.columns(2)
                    with col_btn1:
                        if st.button("✅ Proceed with defaults", type="primary", use_container_width=True):
                            st.session_state['use_defaults_for_missing'] = True
                            st.rerun()
                    with col_btn2:
                        if st.button("❌ Cancel upload", type="secondary", use_container_width=True):
                            st.session_state['uploaded_df'] = None
                            st.session_state['data_ready'] = False
                            return values
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
                st.sidebar.info("Please check that your file is a valid Excel file (.xlsx or .xls)")

    # ===============================
    # MANUAL ENTRY WITH DEFAULTS
    # ===============================
    else:
        # ===============================
        # MANUAL ENTRY WITH DEFAULTS - ORGANIZED BY UNIT
        # ===============================
        st.sidebar.markdown("---")
        #st.sidebar.markdown("### Enter Hospital Metrics")


        # Import BASE_DATA_MANUAL to know which parameters belong to which unit
        from core.constants import BASE_DATA_MANUAL

        # Define unit icons and names
        units_in_order = ['ED', 'WARD', 'STEP', 'ICU']
        unit_icons = {'ED': '🚨', 'WARD': '🛏️', 'STEP': '📉', 'ICU': '💉'}
        unit_names = {
            'ED': 'Emergency Department',
            'WARD': 'General Ward',
            'STEP': 'Step-down / PCU',
            'ICU': 'Intensive Care Unit'}

        # Define display names, units, and help text for each parameter

        param_display = {}
        for param, info in DATA_DICTIONARY.items():
            param_display[param] = {
                'name': info.get('name', ''),
                'unit': info.get('unit', ''),
                'help': info.get('description', f'Enter value for {param.replace("_", " ")}')}

        # Create a mapping from parameter to unit based on BASE_DATA_MANUAL
        param_to_unit = {}
        for unit, params in BASE_DATA_MANUAL.items():
            for param in params:
                param_to_unit[param] = unit

        # Add conditional transfers to ED unit
        conditional_transfers = ['ED_to_ward_admissions', 'ED_to_stepdown_admissions', 'ED_to_ICU_admissions']
        for param in conditional_transfers:
            param_to_unit[param] = 'ED'

        # Group required_data by unit
        params_by_unit = {}
        for var in sorted(required_data):
            unit = param_to_unit.get(var, 'Other')
            if unit not in params_by_unit:
                params_by_unit[unit] = []
            params_by_unit[unit].append(var)

        # Display parameters organized by unit
        for unit in units_in_order:
            if unit in selected_units and unit in params_by_unit and params_by_unit[unit]:
                # Unit header with icon
                st.sidebar.markdown(f"### {unit_icons.get(unit, '📊')} {unit_names.get(unit, unit)}")

                # Create two columns for this unit
                col1, col2 = st.sidebar.columns(2)

                for i, var in enumerate(params_by_unit[unit]):
                    # Get display info - use param_display if available, otherwise create generic
                    if var in param_display:
                        info = param_display[var]
                    else:
                        # Generic fallback for any parameter not in param_display
                        info = {
                            'name': var.replace('_', ' ').title(),
                            'unit': '',
                            'help': f'Enter value for {var.replace("_", " ")}' }

                    display_name = info['name']
                    unit_label = info['unit']
                    help_text = info['help']

                    # Get default value
                    default_val = DEFAULT_VALUES.get(var, 0.0)

                    # Format label with unit
                    if unit_label:
                        label = f"{display_name} ({unit_label})"
                    else:
                        label = display_name

                    # Alternate between columns
                    if i % 2 == 0:
                        with col1:
                            values[var] = st.number_input(label, min_value=0.0, value=default_val,
                                step=1.0, format="%.2f", key=f"manual_{var}", help=help_text)
                    else:
                        with col2:
                            values[var] = st.number_input(label, min_value=0.0, value=default_val,
                                step=1.0, format="%.2f", key=f"manual_{var}", help=help_text )

                st.sidebar.markdown("---")  # Separator between units

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



def get_required_data(selected_units, mode):
    # Choose the correct base data dictionary based on mode
    if mode == "Upload Excel (daily data)":
        base_data = BASE_DATA
    else:
        base_data = BASE_DATA_MANUAL

    required_data = set()
    for u in selected_units:
        required_data.update(base_data.get(u, []))

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


