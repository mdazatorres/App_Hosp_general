
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
```     
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
        
```
            
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
            
| What to Modify                     | Where to Look                                                                 |
|----------------------------------|------------------------------------------------------------------------------|
| Add new input variables          | core/constants.py (BASE_DATA, DATA_DICTIONARY, DEFAULT_VALUES)               |
| Change parameter calculation     | core/parameters.py (compute_parameters_from_entry, compute_parameters_from_excel) |
| Modify equations                 | core/equations_builder.py (build_equations)                                  |
| Change equilibrium solver        | core/equilibrium_solver.py (solve_equilibrium)                               |
| Add surge analysis features      | core/surge_analysis.py (transient_response_for_multi_surge, plot_surge_response) |
| Modify UI layout                 | ui/tabs.py and ui/surge_analysis_tab.py                                      |
| Change documentation             | ui/help_content.py                                                           |
| Add new plots                    | ui/visualizations.py                                                         |
| Change session state variables   | utils/session_manager.py                                                     |
| Add new input mode               | core/data_manager.py (get_operational_inputs) and core/data_processor.py     |