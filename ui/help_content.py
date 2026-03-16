"""Help and documentation content"""

QUICK_START_GUIDE = """
# 🚀 Quick Start Guide

## Getting Started in 3 Simple Steps

### Step 1: Select Your Hospital Units
In the left sidebar, check the boxes for the units you want to include:
- **Emergency Department (ED)** - Patient arrival and initial triage
- **General Ward** - Medical/Surgical and auxiliary beds
- **Step-down / PCU** - Intermediate care unit
- **ICU** - Intensive Care Unit

### Step 2: Enter Your Data
Choose how to provide your hospital data:

**Option A: Manual Entry**
- Select "Manual entry" in the sidebar
- Enter values for each required variable
- Default values are pre-filled

**Option B: Upload Excel**
- Select "Upload Excel (daily data)"
- Upload a file with daily time series data
- Required columns must match the variables shown

### Step 3: Run Analyses
Navigate through the tabs to explore your model:
- **📋 Model Summary** - Shows selected units and equations
- **📊 Parameter Values** - Displays computed parameters
- **⚖️ Equilibrium** - Calculates steady-state occupancy
- **📈 Dynamics** - Simulates changes over time
- **📑 Scenario Analysis** - Compare different scenarios
"""

MODEL_CONFIGURATIONS = """
## 12 Possible Model Configurations

| # | ED | Ward | Step | ICU | Model Name |
|---|:--:|:----:|:----:|:---:|------------|
| 1 | ✅ | ❌ | ❌ | ❌ | ED Only |
| 2 | ✅ | ✅ | ❌ | ❌ | ED + Ward |
| 3 | ✅ | ❌ | ✅ | ❌ | ED + Step-down |
| 4 | ✅ | ❌ | ❌ | ✅ | ED + ICU |
| 5 | ✅ | ✅ | ✅ | ❌ | ED + Ward + Step-down |
| 6 | ✅ | ✅ | ❌ | ✅ | ED + Ward + ICU |
| 7 | ✅ | ❌ | ✅ | ✅ | ED + Step-down + ICU |
| 8 | ✅ | ✅ | ✅ | ✅ | Full Hospital |
| 9 | ❌ | ✅ | ❌ | ❌ | Ward Only |
| 10| ❌ | ✅ | ✅ | ❌ | Ward + Step-down |
| 11| ❌ | ✅ | ❌ | ✅ | Ward + ICU |
| 12| ❌ | ✅ | ✅ | ✅ | Inpatient Units Only |
"""

EQUATIONS_BY_MODEL = """
## Equations by Model Configuration

### Model 1: ED Only

### Model 2: ED + Ward

### Model 8: Full Hospital (All Units)



"""

VARIABLE_DEFINITIONS = """
## Variable Definitions

| Variable | Description | Unit |
|----------|-------------|------|
| **W** | Patients waiting in ED | patients |
| **S** | Patients receiving treatment in ED | patients |
| **B_ward** | Patients boarding for ward bed | patients |
| **B_step** | Patients boarding for step-down bed | patients |
| **B_ICU** | Patients boarding for ICU bed | patients |
| **WARD** | Patients in General Ward | patients |
| **STEP** | Patients in Step-down unit | patients |
| **ICU** | Patients in Intensive Care Unit | patients |

## Parameter Definitions

| Parameter | Description | Unit |
|-----------|-------------|------|
| **λ** | Daily ED arrival rate | patients/day |
| **σ** | Wait time to treatment rate | 1/day |
| **ω** | Left without being seen rate | 1/day |
| **γ** | Treatment completion rate | 1/day |
| **ξ_x** | Boarding transfer rate to unit x | 1/day |
| **μ_x** | Discharge rate from unit x | 1/day |
| **ρ_a→b** | Transfer rate from a to b | 1/day |
| **p_ED→x** | Probability to unit x | dimensionless |
"""





TIPS = """
## Tips for Using the App

### Data Entry Tips
- **Manual Entry**: Default values are provided - just adjust what you need
- **Excel Upload**: Ensure your file has a 'Date' column and all required variables
- **Column Names**: Must match exactly the variable names shown

### Interpretation Tips
- **Equilibrium values** show where the system stabilizes over time
- **Dynamics simulation** shows how the system responds to changes
- **Positive values** indicate patient counts (can't be negative)

### Common Use Cases
1. **Capacity Planning**: See how many beds are needed
2. **What-if Analysis**: Test changes in arrival rates
3. **Bottleneck Identification**: Find over/underutilized units
4. **Discharge Optimization**: See impact of faster discharges
"""



