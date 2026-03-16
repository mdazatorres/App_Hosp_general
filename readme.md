
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
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── create_example_data_set.py      # Script to generate sample data
│
├── core/                           # Core business logic
│   ├── __init__.py
│   ├── dynamics.py                 # Time dynamics simulation
│   ├── equations.py                # ODE equation builder
│   ├── equilibrium.py              # Equilibrium solver
│   ├── manager.py                   # Data management functions
│   ├── parameters.py                # Parameter calculations
│   └── data_processor.py            # Input data processing
│
├── data/                           # Data files and constants
│   ├── __init__.py
│   ├── constants.py                 # System constants and defaults
│   ├── data_example.xlsx            # Example dataset
│   ├── IMPACTS Data Extract_V2.xlsx # Sample hospital data
│   └── Patient Surge Model ED Data.xlsx # ED-specific sample data
│
├── ui/                              # User interface components
│   ├── __init__.py
│   ├── help_content.py               # Help documentation
│   └── tabs.py                        # Tab layouts
│
└── utils/                            # Utility functions
    ├── __init__.py
    ├── helpers.py                      # General helper functions
    └── session.py                       # Session state management