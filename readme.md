
## Overview
This application allows healthcare analysts and hospital administrators to
 model patient flow through different hospital units, calculate key parameters from historical data, and simulate system behavior under various scenarios. The compartment model approach divides the hospital into interconnected units (ED, Ward, Step-down, ICU) with patient flows between them.



## Features
✅ Modular Unit Selection - Choose which hospital units to include in your model
✅ Flexible Data Input - Manual entry or Excel upload with daily time series
✅ Automatic Parameter Calculation - Computes rates and probabilities from your data
✅ Equilibrium Analysis - Finds steady-state patient occupancy
✅ Dynamics Simulation - Visualizes how patient numbers change over time
✅ Comprehensive Documentation - Built-in help and quick start guides
✅ Professional Architecture - Clean separation of concerns for easy maintenance
## Project Structure
hospital_model_app/
│
├── app.py                                    # MAIN ENTRY POINT: Sets up page, initializes session, gets user inputs, creates tabs, calls render functions from ui/tabs.py
├── requirements.txt                          # Python dependencies
├── create_example_data_set.py                # Script to generate sample data
│
├── core/                                     # 🔬 CORE BUSINESS LOGIC
│   ├── __init__.py
│   ├── constants.py                          # Stores all constant data structures (BASE_DATA, DATA_DICTIONARY, DEFAULT_VALUES, ALL_FLOWS)
│   ├── data_manager.py                       # Input handling (get_operational_inputs, get_flows, get_selected_units, get_required_data). Dependencies: core.constants
│   ├── data_processor.py                     # Orchestrates data processing based on input mode (process_input_data(), _process_uploaded_data(),_process_manual_data(), _process_default_data()). Dependencies: core.constants, core.parameters
│   ├── dynamics_simulator.py                 # Time dynamics simulation (simulate_dynamics)
│   ├── equations_builder.py                  # ODE equation builder (build_equations)
│   ├── equilibrium_solver.py                 # Equilibrium solver (solve_equilibrium)
│   ├── parameters.py                         # Parameter calculations (compute_parameters_from_entry, compute_parameters_from_excel)
│   └── surge_analysis.py                     # Surge analysis (build_jacobian, transient_response_for_multi_surge, plot_surge_response, summary_metrics_surge_response)
│
├── data/                                     # 📊 DATA FILES
│   ├── __init__.py
│   ├── data_example.xlsx                     # Example dataset for users
│   ├── IMPACTS Data Extract_V2.xlsx          # Raw hospital data
│   └── Patient Surge Model ED Data.xlsx      # ED-specific data
│
├── ui/                                       # 🎨 USER INTERFACE COMPONENTS
│   ├── __init__.py
│   ├── help_content.py                       # Documentation strings (QUICK_START_GUIDE, MODEL_INFO)
│   ├── surge_analysis_tab.py                 # Surge analysis tab UI (render_surge_analysis_tab). Dependencies: core.surge_analysis
│   ├── tabs.py                               # Main tab layouts (render_model_summary_tab, render_equilibrium_tab, render_dynamics_tab, render_sidebar_info). Dependencies:core.equation_builder, core.constants, ui.visualizations
│   └── visualizations.py                     # Plotting functions (plot_units_comparison, plot_utilization_metrics)
│
└── utils/                                    # 🛠️ UTILITY FUNCTIONS
    ├── __init__.py
    └── session_manager.py                    # Session state management (initialize_session, get_session_value, set_session_value, update_current_params)


            
            ┌─────────────────────────────────────────────────────────────────────────────────┐
            │                                    app.py                                       │
            │  ┌─────────────────────────────────────────────────────────────────────────┐    │
            │  │ initialize_session() → get_selected_units() → get_required_data()       │    │
            │  │                              ↓                                          │    │
            │  │ get_operational_inputs() → process_input_data() → compute_parameters    │    │
            │  │                              ↓                                          │    │
            │  │                    render_*_tab() functions                             │    │
            │  └─────────────────────────────────────────────────────────────────────────┘    │
            └─────────────────────────────────────────────────────────────────────────────────┘
                                                      │
                        ┌─────────────────────────────┼─────────────────────────────┐
                        ▼                             ▼                             ▼
                ┌───────────────────┐    ┌────────────────────┐    ┌───────────────────┐
                │   Model Summary   │    │    Equilibrium     │    │   Surge Analysis  │
                │       Tab         │    │       Tab          │    │       Tab         │
                │                   │    │                    │    │                   │
                │ • Selected units  │    │ • solve_equilibrium│    │ • Define surges   │
                │ • Flow pathways   │    │ • Plot comparison  │    │ • Run simulation  │
                │ • Required data   │    │ • Summary metrics  │    │ • Plot response   │
                │ • ODE equations   │    │                    │    │ • Summary metrics │
                └───────────────────┘    └────────────────────┘    └───────────────────┘

app.py
  ├── core.data_manager
  ├── core.data_processor
  ├── utils.session_manager
  ├── ui.tabs
  ├── ui.help_content
  └── ui.surge_analysis_tab

core.data_manager
  └── core.constants

core.data_processor
  ├── core.constants
  └── core.parameters

core.parameters
  ├── core.constants
  └── core.data_manager (for get_selected_units)

core.equilibrium_solver
  ├── core.equation_builder
  └── core.constants

core.surge_analysis
  └── scipy, numpy, plotly

ui.tabs
  ├── core.equation_builder
  ├── core.constants
  ├── core.equilibrium_solver
  ├── core.dynamics_simulator
  └── ui.visualizations

ui.surge_analysis_tab
  └── core.surge_analysis

ui.visualizations
  └── plotly, pandas


What to Modify	                          Where to Look
Add new input variables	                  core/constants.py (BASE_DATA, DATA_DICTIONARY, DEFAULT_VALUES)
Change parameter calculation	          core/parameters.py (compute_parameters_from_entry, compute_parameters_from_excel)
Modify equations	                      core/equations_builder.py (build_equations)
Change equilibrium solver	              core/equilibrium_solver.py (solve_equilibrium)
Add surge analysis features	              core/surge_analysis.py (transient_response_for_multi_surge, plot_surge_response)
Modify UI layout	                      ui/tabs.py and ui/surge_analysis_tab.py
Change documentation	                  ui/help_content.py
Add new plots	                          ui/visualizations.py
Change session state variables	          utils/session_manager.py
Add new input mode	                      core/data_manager.py (get_operational_inputs) and core/data_processor.py


#######################

"""Constants used throughout the application"""

# Base data requirements for each unit
# BASE_DATA = {"ED": ["daily_ED_arrivals", "left_without_being_seen", "avg_ED_wait_time", "avg_ED_boarding_time",
#            "avg_ED_length_of_stay", "total_adm_from_ED"],
#     "WARD": ["ward_occupied_beds", "ward_discharges", "ward_direct_admission", "ward_transfer_admission", "ward_to_ICU"],
#     "STEP": ["stepdown_occupied_beds", "stepdown_discharges", "stepdown_direct_admission", "stepdown_transfer_admission",
#              "stepdown_to_ICU", "stepdown_to_ward"],
#     "ICU": ["ICU_occupied_beds", "ICU_discharges", "ICU_direct_admission", "ICU_transfer_admission", 'ICU_to_stepdown','ICU_to_ward']}


BASE_DATA = {
    "ED": ["daily_ED_arrivals", "left_without_being_seen", "avg_ED_wait_time",
           "avg_ED_boarding_time", "avg_ED_length_of_stay", "total_adm_from_ED"],
    "WARD": ["ward_occupied_beds", "ward_discharges", "ward_direct_admission",
             "ward_transfer_admission", "ward_to_ICU"],
    "STEP": ["stepdown_occupied_beds", "stepdown_discharges", "stepdown_direct_admission",
             "stepdown_transfer_admission", "stepdown_to_ICU", "stepdown_to_ward"],
    "ICU": ["ICU_occupied_beds", "ICU_discharges", "ICU_direct_admission",
            "ICU_transfer_admission", 'ICU_to_stepdown', 'ICU_to_ward']
}
# Data dictionary with explanations
DATA_DICTIONARY = {
    # ED variables
    'daily_ED_arrivals': {
        'description': 'Average number of patients arriving to the Emergency Department per day',
        'unit': 'patients/day',
        'category': 'ED'
    },
    'left_without_being_seen': {
        'description': 'Average number of patients who leave without being seen per day',
        'unit': 'patients/day',
        'category': 'ED'
    },
    'avg_ED_wait_time': {
        'description': 'Average time patients wait before receiving initial treatment',
        'unit': 'minutes',
        'category': 'ED'
    },
    'avg_ED_boarding_time': {
        'description': 'Average time admitted patients wait for an inpatient bed',
        'unit': 'minutes',
        'category': 'ED'
    },
    'avg_ED_length_of_stay': {
        'description': 'Average total time patients spend in the ED from arrival to discharge or admission',
        'unit': 'minutes',
        'category': 'ED'
    },
    'total_adm_from_ED': {
        'description': 'Average number of patients admitted to the hospital from ED per day',
        'unit': 'patients/day',
        'category': 'ED'
    },
    'ED_to_ward_admissions': {
        'description': 'Average number of ED patients admitted to General Ward per day',
        'unit': 'patients/day',
        'category': 'ED'
    },
    'ED_to_stepdown_admissions': {
        'description': 'Average number of ED patients admitted to Step-down unit per day',
        'unit': 'patients/day',
        'category': 'ED'
    },
    'ED_to_ICU_admissions': {
        'description': 'Average number of ED patients admitted to ICU per day',
        'unit': 'patients/day',
        'category': 'ED'
    },

    # WARD variables
    'ward_occupied_beds': {
        'description': 'Average daily number of occupied beds in the General Ward',
        'unit': 'beds',
        'category': 'WARD'
    },
    'ward_discharges': {
        'description': 'Average number of patients discharged from General Ward per day',
        'unit': 'patients/day',
        'category': 'WARD'
    },
    'ward_direct_admission': {
        'description': 'Average number of patients directly admitted to General Ward (non-ED) per day',
        'unit': 'patients/day',
        'category': 'WARD'
    },
    'ward_transfer_admission': {
        'description': 'Average number of patients transferred into General Ward from other units per day',
        'unit': 'patients/day',
        'category': 'WARD'
    },
    'ward_to_ICU': {
        'description': 'Average number of patients transferred from General Ward to ICU per day',
        'unit': 'patients/day',
        'category': 'WARD'
    },

    # STEP-DOWN variables
    'stepdown_occupied_beds': {
        'description': 'Average daily number of occupied beds in the Step-down unit',
        'unit': 'beds',
        'category': 'STEP'
    },
    'stepdown_discharges': {
        'description': 'Average number of patients discharged from Step-down unit per day',
        'unit': 'patients/day',
        'category': 'STEP'
    },
    'stepdown_direct_admission': {
        'description': 'Average number of patients directly admitted to Step-down unit (non-ED) per day',
        'unit': 'patients/day',
        'category': 'STEP'
    },
    'stepdown_transfer_admission': {
        'description': 'Average number of patients transferred into Step-down unit from other units per day',
        'unit': 'patients/day',
        'category': 'STEP'
    },
    'stepdown_to_ICU': {
        'description': 'Average number of patients transferred from Step-down to ICU per day',
        'unit': 'patients/day',
        'category': 'STEP'
    },
    'stepdown_to_ward': {
        'description': 'Average number of patients transferred from Step-down to General Ward per day',
        'unit': 'patients/day',
        'category': 'STEP'
    },

    # ICU variables
    'ICU_occupied_beds': {
        'description': 'Average daily number of occupied beds in the ICU',
        'unit': 'beds',
        'category': 'ICU'
    },
    'ICU_discharges': {
        'description': 'Average number of patients discharged from ICU per day',
        'unit': 'patients/day',
        'category': 'ICU'
    },
    'ICU_direct_admission': {
        'description': 'Average number of patients directly admitted to ICU (non-ED) per day',
        'unit': 'patients/day',
        'category': 'ICU'
    },
    'ICU_transfer_admission': {
        'description': 'Average number of patients transferred into ICU from other units per day',
        'unit': 'patients/day',
        'category': 'ICU'
    },
    'ICU_to_stepdown': {
        'description': 'Average number of patients transferred from ICU to Step-down per day',
        'unit': 'patients/day',
        'category': 'ICU'
    },
    'ICU_to_ward': {
        'description': 'Average number of patients transferred from ICU to General Ward per day',
        'unit': 'patients/day',
        'category': 'ICU'
    }
}

# Default values for all parameters
DEFAULT_VALUES = {
        # ED defaults
        'daily_ED_arrivals': 270.82,
        'left_without_being_seen': 7.15,
        'avg_ED_wait_time': 112.59,
        'avg_ED_boarding_time': 973.72,
        'avg_ED_length_of_stay': 456.33,
        'total_adm_from_ED': 50.02,
        'ED_to_ward_admissions': 35.04,
        'ED_to_stepdown_admissions': 1.44,
        'ED_to_ICU_admissions': 6.58,
#
        # Ward defaults
        'ward_occupied_beds': 400.33,
        'ward_discharges': 66.37,
        'ward_direct_admission': 9.27,
        'ward_direct_admission_avg': 9.27,
        'ward_transfer_admission': 7.63,
        'ward_transfer_admission_avg': 7.63,
        'ward_to_ICU':  2.98,

        # Step-down defaults
        'stepdown_occupied_beds': 8.39,
        'stepdown_discharges': 2.33,
        'stepdown_direct_admission': 5.28,
        'stepdown_direct_admission_avg': 5.28,
        'stepdown_transfer_admission': 0.59,
        'stepdown_transfer_admission_avg': 0.59,
        'stepdown_to_ICU': 0.78,
        'stepdown_to_ward': 3.52, # check this

        # ICU defaults
        'ICU_occupied_beds': 76.94,
        'ICU_discharges': 3.05,
        'ICU_direct_admission': 2.00, # I add 0.5
        'ICU_direct_admission_avg': 2.00,
        'ICU_transfer_admission': 3.37,
        'ICU_transfer_admission_avg': 3.37,
        'ICU_to_stepdown': 0.1,
        'ICU_to_ward': 12.80,
    }


# All possible flows between units
ALL_FLOWS = [
    ("ED", "WARD"), ("ED", "STEP"), ("ED", "ICU"),
    ("WARD", "ICU"), ("ICU", "WARD"), ("WARD", "STEP"),
    ("STEP", "WARD"), ("ICU", "STEP"), ("STEP", "ICU")
]

default_params_ = {
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


default_params = {

'daily_ED_arrivals_avg': 270.82,
1/'sigma': 1/12.78,   avg_ED_wait_time
'omega': 0.34,   calculate 
'gamma': 9.056,  average treatment time in ED
or 'total_adm_from_ED', 'left_without_being_seen'

'pED_to_step': 0.005464344528170069, calculate or 
'pED_to_ward': 0.1329074970474242,   calculate or
'pED_to_ICU': 0.024976296222366384,  calculate or
'1/xi_ICU': 1/1.4788523039502726, # ICU boarding time until have a bed
'1/xi_ward': 1/1.4788523039502726, # Ward boarding time until have a bed
'1/xi_step': 1/1.4788523039502726, # Step boarding time until have a bed

# Ward parameters
'1/ward_discharge_rate': 1/0.165809381385132, # length of stay in ward until discharge
'1/ward_to_ICU_rate': 1/0.0074498912644547065, # length of stay in ward until go to ICU
'ward_direct_admission_avg': 9.28,
'ward_transfer_admission_avg': 7.64,

    # Step-down parameters
'1/step_discharge_rate': 1/0.27873563218390807, # length of stay in step until discharge
'1/step_to_ICU_rate': 0.09299895506792058,    # length of stay in step until go to ICU
'1/step_to_ward_rate': 0.42,                 # length of stay in step until go to ward
'stepdown_direct_admission_avg': 5.28,
'stepdown_transfer_admission_avg': 0.60,

    # ICU parameters
'1/ICU_discharge_rate': 1/0.03964318285453716, # length of stay in ICU until discharge
'1/ICU_to_ward_rate': 1/0.16638166894664844,   # length of stay in ICU until go ward
'1/ICU_to_step_rate': 1/0.0013109895120839033, # length of stay in ICU until go step
'ICU_direct_admission_avg': 2.00,
'ICU_transfer_admission_avg': 3.37,
}