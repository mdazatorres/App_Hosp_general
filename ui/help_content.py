"""Help and documentation content"""

QUICK_START_GUIDE = """
### 🚀 Quick Start Guide

This guide will help you get started with the Hospital Compartment Model Builder in three simple steps.

---

#### Step 1: Select Your Hospital Units

In the left sidebar, check the boxes for the units you want to include in your model:

| Unit | Description |
|------|-------------|
| **Emergency Department (ED)** | Patient arrival, triage, initial treatment, and boarding |
| **General Ward** | Medical/Surgical and auxiliary beds for non-critical patients |
| **Step-down** | Intermediate care unit for patients transitioning between ICU and ward. **Flexible use:** Can also represent other inpatient units such as Telemetry, Progressive Care, or Specialty Units (e.g., Oncology, Orthopedics, Neurology)
| **ICU** | Intensive Care Unit for critically ill patients requiring high-acuity care |

✅ **Once you've selected your units**, the app automatically determines which parameters are required for your specific configuration.

###### 💡 *Tip*: Not sure which configuration to choose? Visit the **Model Documentation** tab to explore all 12 possible model configurations and find the one that best fits your analysis needs.
---

#### Step 2: Enter Your Data

You can provide hospital data in two ways:

##### Option A: Manual Entry
1. Select **"Manual entry"** in the sidebar
2. Enter values for each required variable in the input fields
3. Default values are pre-filled based on typical hospital data—adjust them as needed
4. All input fields show the variable name and expected units

##### Option B: Upload Excel
1. Select **"Upload Excel (daily data)"** in the sidebar
2. Upload a file with daily time series data (must include a **'Date'** column)
3. The app will automatically:
   - Verify that all required columns are present
   - Compute daily averages or sums as appropriate
   - Display a preview of your data
4. If some columns are missing, the app will show which ones are required

> ⚠️ **Note**: If you don't provide some of the required data, the app will use pre-determined default values and notify you. For accurate results, we recommend providing complete data.

---

#### Step 3: Run Analyses

Navigate through the tabs to explore your model:

| Tab | Purpose |
|-----|---------|
| **📋 Model Summary** | Review your selected units, patient flow pathways, required data inputs, and the complete ODE system for your model |
| **⚖️ Equilibrium** | Calculate steady-state occupancy levels. This shows where the system would stabilize under constant conditions—useful for validating against historical averages |
| **📑 Scenario Analysis** | Test the impact of surge events. Define when and how much patient inflow increases in specific units, and see how this affects bed demand across the hospital |
| **📚 Documentation** | Access the Quick Start guide (this page) and Model Theory documentation |

---

#### Step 4: Create Your Surge Scenario

The **Scenario Analysis** tab allows you to simulate surge events and quantify their impact on hospital capacity.

##### Defining Surge Events

For each inpatient unit (WARD, STEP, ICU), you can define **multiple surge events** with:

| Parameter | Description |
|-----------|-------------|
| **Start Day** | When the surge begins (in days) |
| **End Day** | When the surge ends (in days) |
| **Amplitude** | How many extra patients per day are added to direct admissions |

💡 **Tip**: Multiple surges can overlap, and their effects are summed linearly. You can define up to 5 surge events per unit.

##### Interpreting the Results

| Metric | What It Represents | Why It Matters |
|--------|-------------------|----------------|
| **Peak Additional Beds** | Maximum extra patients in each unit during the surge | **Planning peak capacity needs** for surge periods |
| **Extra Bed-Days** | Total cumulative workload (sum of daily extra beds) | **Resource allocation and staffing** requirements |
| **Peak System Load** | Maximum total patients relative to baseline | **Overall system stress** and bottleneck identification |
| **Recovery Time** | How long until system returns to baseline | **Duration of surge impact** and when operations normalize |

#### Example Interpretation

If your analysis shows:
- **WARD**: Peak +15 beds, 268 extra bed-days
- **STEP**: Peak +2 beds, 23 extra bed-days
- **ICU**: Peak +3 beds, 25 extra bed-days

This means:
- At the worst point, you need **15 additional ward beds**
- The **total workload** for ward staff is equivalent to 268 bed-days
- The **ICU** experiences a smaller but still significant surge
- The **step-down unit** requires minimal additional capacity

---

#### What's Next?

After following these steps, you can:

| Action | Purpose |
|--------|---------|
| **Validate your model** | Compare equilibrium results with historical data to ensure accuracy |
| **Run surge scenarios** | Test different surge patterns (varying timing, duration, amplitude) to plan for capacity needs |
| **Analyze results** | Review peak bed requirements, total extra bed-days, and recovery times |
| **Refine parameters** | Adjust input values to match your specific hospital context |
| **Export results** | Use the simulation outputs for planning reports and presentations |


"""



MODEL_INFO = r""" ### 🏥 Hospital Surge Capacity Model

The main purpose of this work is to **predict bed requirements during surge events**. 
This model allows us to simulate hospital dynamics under routine conditions and quantify how
 much the system deviates from equilibrium when faced with increased demand in specific clinical units.

**Key capabilities:**
- **Quantify additional bed capacity** required to accommodate elevated demand
- **Describe system evolution** toward a new steady state under prolonged surges
- **Provide actionable insights** for hospital administrators and emergency planners


#### Model overview

We developed a compartmental system dynamics model that represents the hospital as an interconnected network of clinical units through which patients flow—from emergency intake or direct admission to inpatient wards, intensive care units, step-down units, and ultimately discharge. By emphasizing patient movement between units rather than detailed unit-level operations, the framework captures hospital-wide dynamics in a manner that is both analytically tractable and readily interpretable.

The model captures net transitions among stages of care and bed types, reflecting the evolving occupancy dynamics of the hospital. It can be configured to include different combinations of clinical units depending on the analysis needs.
| Component | Description |
|-----------|-------------|
| **Emergency Department** | Arrivals, triage, treatment, boarding, and left-without-being-seen |
| **Direct Admissions** | Patients admitted directly to inpatient units (non-ED) |
| **Inter-facility Transfers** | Patients transferred from other hospitals |
| **General Ward** | Medical/Surgical and auxiliary beds |
| **Step-down / PCU** | Intermediate care unit for transitioning patients |
| **ICU** | Intensive Care Unit for critically ill patients |
| **Discharge** | Patients exiting the hospital system |

Rather than modeling every operational detail, the framework focuses on **net patient flows**, allowing equilibrium states to be explicitly characterized and systematically perturbed by surge events.

#### Model Configurations
The framework supports **12 distinct hospital configurations** based on which clinical units are included. The table below summarizes all possible configurations (✅ = included, ❌ = excluded).

| # | ED | Ward | Step | ICU | Model Name | Description |
|---|:--:|:----:|:----:|:---:|------------|-------------|
| 1 | ✅ | ❌ | ❌ | ❌ | **ED Only** | Emergency Department flow without inpatient units |
| 2 | ✅ | ✅ | ❌ | ❌ | **ED + Ward** | ED with general ward (no step-down or ICU) |
| 3 | ✅ | ❌ | ✅ | ❌ | **ED + Step-down** | ED with intermediate care unit |
| 4 | ✅ | ❌ | ❌ | ✅ | **ED + ICU** | ED with intensive care unit |
| 5 | ✅ | ✅ | ✅ | ❌ | **ED + Ward + Step-down** | ED with general ward and step-down unit |
| 6 | ✅ | ✅ | ❌ | ✅ | **ED + Ward + ICU** | ED with general ward and ICU (no step-down) |
| 7 | ✅ | ❌ | ✅ | ✅ | **ED + Step-down + ICU** | ED with step-down and ICU (no general ward) |
| 8 | ✅ | ✅ | ✅ | ✅ | **Full Hospital** | Complete hospital system with all units |
| 9 | ❌ | ✅ | ❌ | ❌ | **Ward Only** | Standalone general ward |
| 10| ❌ | ✅ | ✅ | ❌ | **Ward + Step-down** | General ward with step-down unit |
| 11| ❌ | ✅ | ❌ | ✅ | **Ward + ICU** | General ward with ICU (direct admissions only) |
| 12| ❌ | ✅ | ✅ | ✅ | **Inpatient Units Only** | All inpatient units without ED |


#### Model Equations
The governing ordinary differential equations  for each configuration are presented below. These equations describe how patient counts evolve over time in each compartment. The notation follows standard conventions where:

- **State Variables** represent patient counts in each compartment
- **Parameters** represent rates and probabilities governing patient flow
- **Inputs** represent external admissions and transfers

##### 1. ED Only

This configuration captures the basic dynamics of the Emergency Department, including patient arrivals, waiting, treatment, and departures (either discharged or left without being seen).

$$
\begin{aligned}
\frac{dW}{dt} &= \lambda - (\sigma + \omega) W \\[4pt]
\frac{dS}{dt} &= \sigma W - \gamma S
\end{aligned}
$$

**Interpretation:** Patients arrive at rate $\lambda$ to the waiting area ($W$). They transition to treatment ($S$) at rate $\sigma$, or leave without being seen at rate $\omega$. From treatment, patients complete care and exit the system at rate $\gamma$.

---

##### 2. ED + Ward

This configuration adds a general ward ($\text{WARD}$) to the ED model. Admitted patients first wait in a boarding area ($B_{\text{ward}}$) before being transferred to the ward.

$$
\begin{aligned}
\frac{dW}{dt} &= \lambda - (\sigma + \omega) W \\[4pt]
\frac{dS}{dt} &= \sigma W - \gamma S \\[4pt]
\frac{dB_{\text{ward}}}{dt} &= p_{\text{ED}\to\text{ward}} \, \gamma S - \xi_{\text{ward}} \, B_{\text{ward}} \\[4pt]
\frac{d\text{WARD}}{dt} &= A_{\text{ward}} + T_{\text{ward}} + \xi_{\text{ward}} \, B_{\text{ward}} - \mu_{\text{ward}} \, \text{WARD}
\end{aligned}
$$

**Interpretation:** A fraction $p_{\text{ED}\to\text{ward}}$ of patients completing ED treatment require admission to the ward. They enter a boarding queue ($B_{\text{ward}}$) and transfer to the ward at rate $\xi_{\text{ward}}$. The ward also receives direct admissions ($A_{\text{ward}}^{\text{dir}}$) and external transfers ($T_{\text{ward}}$). Patients exit the ward via discharge at rate $\mu_{\text{ward}}$.

---

##### 3. ED + Step-down
This configuration replaces the general ward with a step-down/intermediate care unit ($\text{STEP}$).

$$
\begin{aligned}
\frac{dW}{dt} &= \lambda - (\sigma + \omega) W \\[4pt]
\frac{dS}{dt} &= \sigma W - \gamma S \\[4pt]
\frac{dB_{\text{step}}}{dt} &= p_{\text{ED}\to\text{step}} \, \gamma S - \xi_{\text{step}} \, B_{\text{step}} \\[4pt]
\frac{d\text{STEP}}{dt} &= A_{\text{step}} + T_{\text{step}} + \xi_{\text{step}} \, B_{\text{step}} - \mu_{\text{step}} \, \text{STEP}
\end{aligned}
$$

**Interpretation:** Similar to the ED + Ward configuration, but with step-down unit-specific admission probability and boarding rate.

---

##### 4. ED + ICU
This configuration adds an Intensive Care Unit ($\text{ICU}$) to the ED model.

$$
\begin{aligned}
\frac{dW}{dt} &= \lambda - (\sigma + \omega) W \\[4pt]
\frac{dS}{dt} &= \sigma W - \gamma S \\[4pt]
\frac{dB_{\text{ICU}}}{dt} &= p_{\text{ED}\to\text{ICU}} \, \gamma S - \xi_{\text{ICU}} \, B_{\text{ICU}} \\[4pt]
\frac{d\text{ICU}}{dt} &= A_{\text{ICU}} + T_{\text{ICU}} + \xi_{\text{ICU}} \, B_{\text{ICU}} - \mu_{\text{ICU}} \, \text{ICU}
\end{aligned}
$$

**Interpretation:** Critically ill patients requiring ICU admission are routed accordingly, with ICU-specific boarding and discharge processes.

---

##### 5. ED + Ward + Step-down

This configuration includes both general ward and step-down units, allowing patients to be admitted to either unit based on clinical need.

$$
\begin{aligned}
\frac{dW}{dt} &= \lambda - (\sigma + \omega) W \\[4pt]
\frac{dS}{dt} &= \sigma W - \gamma S \\[4pt]
\frac{dB_{\text{ward}}}{dt} &= p_{\text{ED}\to\text{ward}} \, \gamma S - \xi_{\text{ward}} \, B_{\text{ward}} \\[4pt]
\frac{dB_{\text{step}}}{dt} &= p_{\text{ED}\to\text{step}} \, \gamma S - \xi_{\text{step}} \, B_{\text{step}} \\[4pt]
\frac{d\text{WARD}}{dt} &= A_{\text{ward}} + T_{\text{ward}} + \xi_{\text{ward}} \, B_{\text{ward}} + \rho_{\text{step}\to\text{ward}} \, \text{STEP} - (\mu_{\text{ward}} + \rho_{\text{ward}\to\text{ICU}}) \, \text{WARD} \\[4pt]
\frac{d\text{STEP}}{dt} &= A_{\text{step}} + T_{\text{step}} + \xi_{\text{step}} \, B_{\text{step}} - (\mu_{\text{step}} + \rho_{\text{step}\to\text{ward}} + \rho_{\text{step}\to\text{ICU}}) \, \text{STEP}
\end{aligned}
$$

**Interpretation:** Patients can flow between the ward and step-down units. The step-down unit may transfer patients to the ward ($\rho_{\text{step}\to\text{ward}}$), representing clinical improvement. Ward patients may also be transferred to ICU (when ICU is present).


---

##### 6. ED + Ward + ICU
This configuration includes general ward and ICU, allowing transfers between these units.

$$
\begin{aligned}
\frac{dW}{dt} &= \lambda - (\sigma + \omega) W \\[4pt]
\frac{dS}{dt} &= \sigma W - \gamma S \\[4pt]
\frac{dB_{\text{ward}}}{dt} &= p_{\text{ED}\to\text{ward}} \, \gamma S - \xi_{\text{ward}} \, B_{\text{ward}} \\[4pt]
\frac{dB_{\text{ICU}}}{dt} &= p_{\text{ED}\to\text{ICU}} \, \gamma S - \xi_{\text{ICU}} \, B_{\text{ICU}} \\[4pt]
\frac{d\text{WARD}}{dt} &= A_{\text{ward}} + T_{\text{ward}} + \xi_{\text{ward}} \, B_{\text{ward}} + \rho_{\text{ICU}\to\text{ward}} \, \text{ICU} - (\mu_{\text{ward}} + \rho_{\text{ward}\to\text{ICU}}) \, \text{WARD} \\[4pt]
\frac{d\text{ICU}}{dt} &= A_{\text{ICU}} + T_{\text{ICU}} + \xi_{\text{ICU}} \, B_{\text{ICU}} + \rho_{\text{ward}\to\text{ICU}} \, \text{WARD} - (\mu_{\text{ICU}} + \rho_{\text{ICU}\to\text{ward}}) \, \text{ICU}
\end{aligned}
$$

**Interpretation:** Bi-directional patient flow exists between the ward and ICU. Patients may transfer to ICU due to clinical deterioration ($\rho_{\text{ward}\to\text{ICU}}$), or step down to the ward upon improvement ($\rho_{\text{ICU}\to\text{ward}}$).

---

##### 7. ED + Step-down + ICU
This configuration includes step-down and ICU units, with transfers between them.

$$
\begin{aligned}
\frac{dW}{dt} &= \lambda - (\sigma + \omega) W \\[4pt]
\frac{dS}{dt} &= \sigma W - \gamma S \\[4pt]
\frac{dB_{\text{step}}}{dt} &= p_{\text{ED}\to\text{step}} \, \gamma S - \xi_{\text{step}} \, B_{\text{step}} \\[4pt]
\frac{dB_{\text{ICU}}}{dt} &= p_{\text{ED}\to\text{ICU}} \, \gamma S - \xi_{\text{ICU}} \, B_{\text{ICU}} \\[4pt]
\frac{d\text{STEP}}{dt} &= A_{\text{step}} + T_{\text{step}} + \xi_{\text{step}} \, B_{\text{step}} + \rho_{\text{ICU}\to\text{step}} \, \text{ICU} - (\mu_{\text{step}} + \rho_{\text{step}\to\text{ward}} + \rho_{\text{step}\to\text{ICU}}) \, \text{STEP} \\[4pt]
\frac{d\text{ICU}}{dt} &= A_{\text{ICU}} + T_{\text{ICU}} + \xi_{\text{ICU}} \, B_{\text{ICU}} + \rho_{\text{step}\to\text{ICU}} \, \text{STEP} - (\mu_{\text{ICU}} + \rho_{\text{ICU}\to\text{step}} + \rho_{\text{ICU}\to\text{ward}}) \, \text{ICU}
\end{aligned}
$$

**Interpretation:** Patients can transfer between step-down and ICU units in both directions, representing the typical progression of critically ill patients.

---

##### 8. Full Hospital (All Units)
This is the complete model incorporating all clinical units: ED, Ward, Step-down, and ICU. It captures the full complexity of patient flow through the hospital system, including all possible transfer pathways between units.

**Interpretation:** This comprehensive model captures all patient flows within a typical hospital, including ED-to-unit admissions, inter-unit transfers, and discharges. It is suitable for analyzing complex hospital-wide dynamics and capacity planning.

$$
\begin{aligned}
\frac{dW}{dt} &= \lambda - (\sigma + \omega) W \\[4pt]
\frac{dS}{dt} &= \sigma W - \gamma S \\[4pt]
\frac{dB_{\text{ward}}}{dt} &= p_{\text{ED}\to\text{ward}} \, \gamma S - \xi_{\text{ward}} \, B_{\text{ward}} \\[4pt]
\frac{dB_{\text{step}}}{dt} &= p_{\text{ED}\to\text{step}} \, \gamma S - \xi_{\text{step}} \, B_{\text{step}} \\[4pt]
\frac{dB_{\text{ICU}}}{dt} &= p_{\text{ED}\to\text{ICU}} \, \gamma S - \xi_{\text{ICU}} \, B_{\text{ICU}} \\[4pt]
\frac{d\text{WARD}}{dt} &= A_{\text{ward}} + T_{\text{ward}} + \xi_{\text{ward}} \, B_{\text{ward}} + \rho_{\text{ICU}\to\text{ward}} \, \text{ICU} + \rho_{\text{step}\to\text{ward}} \, \text{STEP} \\[2pt]
&\quad - (\mu_{\text{ward}} + \rho_{\text{ward}\to\text{ICU}}) \, \text{WARD} \\[8pt]
\frac{d\text{STEP}}{dt} &= A_{\text{step}} + T_{\text{step}} + \xi_{\text{step}} \, B_{\text{step}} + \rho_{\text{ICU}\to\text{step}} \, \text{ICU} \\[2pt]
&\quad - (\mu_{\text{step}} + \rho_{\text{step}\to\text{ICU}} + \rho_{\text{step}\to\text{ward}}) \, \text{STEP} \\[8pt]
\frac{d\text{ICU}}{dt} &= A_{\text{ICU}} + T_{\text{ICU}} + \xi_{\text{ICU}} \, B_{\text{ICU}} + \rho_{\text{ward}\to\text{ICU}} \, \text{WARD} + \rho_{\text{step}\to\text{ICU}} \, \text{STEP} \\[2pt]
&\quad - (\mu_{\text{ICU}} + \rho_{\text{ICU}\to\text{ward}} + \rho_{\text{ICU}\to\text{step}}) \, \text{ICU}
\end{aligned}
$$

---

##### 9. Ward Only
This simplified configuration models the general ward in isolation, useful for analyzing ward-level dynamics without the influence of other units.

$$
\begin{aligned}
\frac{d\text{WARD}}{dt} &= A_{\text{ward}} + T_{\text{ward}} - \mu_{\text{ward}} \, \text{WARD}
\end{aligned}
$$

---

##### 10. Ward + Step-down
This configuration captures the interaction between general ward and step-down units, with unidirectional flow from step-down to ward.

$$
\begin{aligned}
\frac{d\text{WARD}}{dt} &= A_{\text{ward}} + T_{\text{ward}} + \rho_{\text{step}\to\text{ward}} \, \text{STEP} - (\mu_{\text{ward}} + \rho_{\text{ward}\to\text{ICU}}) \, \text{WARD} \\[8pt]
\frac{d\text{STEP}}{dt} &= A_{\text{step}} + T_{\text{step}} - (\mu_{\text{step}} + \rho_{\text{step}\to\text{ward}}) \, \text{STEP}
\end{aligned}
$$

---

##### 11. Ward + ICU
This configuration captures bi-directional transfers between ward and ICU, typical of patients requiring escalation or de-escalation of care.
$$
\begin{aligned}
\frac{d\text{WARD}}{dt} &= A_{\text{ward}} + T_{\text{ward}} + \rho_{\text{ICU}\to\text{ward}} \, \text{ICU} - (\mu_{\text{ward}} + \rho_{\text{ward}\to\text{ICU}}) \, \text{WARD} \\[8pt]
\frac{d\text{ICU}}{dt} &= A_{\text{ICU}} + T_{\text{ICU}} + \rho_{\text{ward}\to\text{ICU}} \, \text{WARD} - (\mu_{\text{ICU}} + \rho_{\text{ICU}\to\text{ward}}) \, \text{ICU}
\end{aligned}
$$

---

##### 12. Inpatient Units Only (Ward + Step-down + ICU)
This configuration models the complete inpatient system without the Emergency Department. All admissions come from direct admissions or external transfers, representing scenarios where ED inflow is not of interest or is already accounted for.
$$
\begin{aligned}
\frac{d\text{WARD}}{dt} &= A_{\text{ward}} + T_{\text{ward}} + \rho_{\text{ICU}\to\text{ward}} \, \text{ICU} + \rho_{\text{step}\to\text{ward}} \, \text{STEP} \\[2pt]
&\quad - (\mu_{\text{ward}} + \rho_{\text{ward}\to\text{ICU}}) \, \text{WARD} \\[8pt]
\frac{d\text{STEP}}{dt} &= A_{\text{step}} + T_{\text{step}} + \rho_{\text{ICU}\to\text{step}} \, \text{ICU} \\[2pt]
&\quad - (\mu_{\text{step}} + \rho_{\text{step}\to\text{ICU}} + \rho_{\text{step}\to\text{ward}}) \, \text{STEP} \\[8pt]
\frac{d\text{ICU}}{dt} &= A_{\text{ICU}} + T_{\text{ICU}} + \rho_{\text{ward}\to\text{ICU}} \, \text{WARD} + \rho_{\text{step}\to\text{ICU}} \, \text{STEP} \\[2pt]
&\quad - (\mu_{\text{ICU}} + \rho_{\text{ICU}\to\text{ward}} + \rho_{\text{ICU}\to\text{step}}) \, \text{ICU}
\end{aligned}
$$



#### Parameter Definitions and Interpretation
The following table defines all parameters used in the model equations, along with their typical ranges and clinical interpretations.

| Parameter | Description | Typical Range | Interpretation |
|-----------|-------------|---------------|----------------|
| **ED Parameters** ||||
| $\lambda$ | Daily ED arrival rate | 50-500 patients/day | Volume of patients entering the ED |
| $\sigma$ | Wait time to treatment rate | 1-4 per day | Inverse of average waiting time. Higher $\sigma$ means faster triage |
| $\omega$ | Left without being seen rate | 0-0.5 per day | Rate at which patients leave without treatment. $\omega = \sigma \cdot f/(1-f)$ where $f$ is fraction leaving |
| $\gamma$ | Treatment completion rate | 0.5-4 per day | Inverse of average treatment time in ED |
| $p_{\text{ED}\to\text{ward}}$ | Probability ED patient goes to ward | 0.1-0.5 | Fraction of admitted ED patients sent to general ward |
| $p_{\text{ED}\to\text{step}}$ | Probability ED patient goes to step-down | 0.05-0.2 | Fraction admitted to step-down/PCU |
| $p_{\text{ED}\to\text{ICU}}$ | Probability ED patient goes to ICU | 0.02-0.15 | Fraction admitted to ICU |
| $\xi_{\text{ward}}$ | Ward boarding transfer rate | 0.5-4 per day | Rate at which boarded patients transfer from ED to ward |
| $\xi_{\text{step}}$ | Step-down boarding transfer rate | 0.5-4 per day | Rate at which boarded patients transfer to step-down |
| $\xi_{\text{ICU}}$ | ICU boarding transfer rate | 0.5-4 per day | Rate at which boarded patients transfer to ICU |
| **Ward Parameters** ||||
| $\mu_{\text{ward}}$ | Ward discharge rate | 0.1-1 per day | Inverse of average length of stay in ward |
| $\rho_{\text{ward}\to\text{ICU}}$ | Ward to ICU transfer rate | 0-0.2 per day | Rate of transfers from ward to ICU due to clinical deterioration |
| $A_{\text{ward}}$ | Direct admissions to ward | 0-50 patients/day | Patients admitted directly to ward (non-ED) |
| $T_{\text{ward}}$ | External transfers to ward | 0-20 patients/day | Patients transferred from other hospitals to ward |
| **Step-down Parameters** ||||
| $\mu_{\text{step}}$ | Step-down discharge rate | 0.2-1 per day | Inverse of average length of stay in step-down |
| $\rho_{\text{step}\to\text{ICU}}$ | Step-down to ICU transfer rate | 0-0.2 per day | Rate of transfers from step-down to ICU |
| $\rho_{\text{step}\to\text{ward}}$ | Step-down to ward transfer rate | 0-0.3 per day | Rate of patients stepping down from ICU to step-down or step-down to ward |
| $A_{\text{step}}$ | Direct admissions to step-down | 0-30 patients/day | Patients admitted directly to step-down |
| $T_{\text{step}}$ | External transfers to step-down | 0-10 patients/day | Patients transferred from other hospitals to step-down |
| **ICU Parameters** ||||
| $\mu_{\text{ICU}}$ | ICU discharge rate | 0.1-0.5 per day | Inverse of average length of stay in ICU |
| $\rho_{\text{ICU}\to\text{ward}}$ | ICU to ward transfer rate | 0.1-0.4 per day | Rate of transfers from ICU to ward |
| $\rho_{\text{ICU}\to\text{step}}$ | ICU to step-down transfer rate | 0.05-0.2 per day | Rate of transfers from ICU to step-down |
| $A_{\text{ICU}}$ | Direct admissions to ICU | 0-20 patients/day | Patients admitted directly to ICU |
| $T_{\text{ICU}}$ | External transfers to ICU | 0-10 patients/day | Patients transferred from other hospitals to ICU |


#### Core Assumption: Near-Equilibrium Operation

The model assumes that hospitals operate near a **dynamic equilibrium** under routine conditions. This baseline equilibrium is characterized by:

- Constant arrival rates ($\lambda$)
- Stable service times ($1/\gamma$)
- Predictable boarding delays ($1/\xi_{\cdot}$)
- Consistent admission probabilities ($p_{ED\to\text{unit}}$)

These baseline conditions are derived from historical data and represent "normal" hospital operations.

---

#### Surge Analysis: Understanding Demand Increases

We focus on scenarios where a sustained influx of patients bypasses the Emergency Department and is routed directly to inpatient units:
- **Step-down Unit ($STEP$)**
- **General Ward ($WARD$)**
- **ICU ($ICU$)**

**Examples:** Mass-casualty incidents, coordinated disaster responses, pandemic surges, conflict-related patient influxes

##### Key Assumption

**ED operations remain at baseline equilibrium throughout the surge event.** This means:
- ED arrival rates ($\lambda$) are unchanged
- Service times ($1/\gamma$) are unchanged
- Boarding delays ($1/\xi_{\cdot}$) are unchanged
- Admission proportions ($p_{ED\to\text{unit}}$) are unchanged

This assumption reflects a critical objective: **determine the additional inpatient bed capacity required to absorb the surge WITHOUT disrupting routine ED functioning.** In other words, the hospital continues processing the same volume of ED patients as normal while simultaneously accommodating excess direct admissions.

Mathematical Formulation of this model can be found in [REF]


---



### Limitations & Assumptions

1. **Linear Approximation**: Surge analysis uses linearization around equilibrium, valid for small-to-moderate perturbations
2. **Constant Rates**: All transition rates are assumed constant during the surge
3. **No ED Feedback**: Assumes ED operations unaffected by inpatient congestion
4. **Homogeneous Patients**: Patients within each unit are treated as identical
5. **No Capacity Constraints**: Model predicts demand without imposing hard bed limits

These assumptions make the model analytically tractable while providing valuable planning insights.

"""