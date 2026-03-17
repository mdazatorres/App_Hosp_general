"""
EXAMPLE DATA SET GENERATOR AND VALIDATION TOOL
===============================================
This script serves two purposes:
1. Creates example datasets for the Hospital Compartment Model Builder app
2. Provides independent validation of model calculations (separate from the app)

The computed values here (parameters and equilibrium) can be used to verify
that the app is working correctly.
"""


import numpy as np
import pandas as pd


# =============================================================================
# PART 1: DATA PROCESSING - Load and merge raw data files
# =============================================================================
def procces_data(init_day='2024-03-31', end_day='2025-03-31'):
    xls = pd.ExcelFile("data/IMPACTS Data Extract_V2.xlsx")
    data_ED = pd.read_excel('data/Patient Surge Model ED Data.xlsx')

    df_capacity = pd.read_excel(xls, sheet_name="Capacity")
    df_OR = pd.read_excel(xls, sheet_name="OR")

    df_adt = pd.read_excel(xls, sheet_name="ADT Summary")
    df_adt_all = pd.read_excel(xls, sheet_name="Admission Breakdown")

    # The data set V2 going beyond 2025-03-31, in order to merge all data sets at the same date with load data until that time
    df_adt_all = df_adt_all[df_adt_all.ADMIT_DATE <= '2025-03-31']
    df_ICU_downUp = pd.read_excel(xls, sheet_name='ICU DownUp')

    df_capacity = df_capacity.rename({'DAY_DT': 'Date'}, axis=1)
    df_OR = df_OR.rename({'DateValue': 'Date'}, axis=1)
    df_adt = df_adt.rename({'DateValue': 'Date'}, axis=1)

    df_adt_all = df_adt_all.rename(columns={"ADMIT_DATE": "Date"})
    data_ED = data_ED.rename(columns={'ED_ARRIVAL_IMPUTED_DT': "Date"})
    df_ICU_downUp = df_ICU_downUp.rename({'Transfer_Date': 'Date'}, axis=1)
    df_ICU_downUp = df_ICU_downUp[df_ICU_downUp['Date'] <= '2025-03-31'].copy()

    df = pd.merge(df_adt_all, data_ED, on='Date')
    df = pd.merge(df, df_capacity, on='Date')
    df = pd.merge(df, df_ICU_downUp, on='Date')
    df = pd.merge(df, df_adt, on='Date')
    df = pd.merge(df, df_OR, on='Date')

    df = df.sort_values(by='Date').reset_index(drop=True)
    df = df[df['Date'] >= init_day]
    df = df[df['Date'] <= end_day]
    # Convert to day the ED waiting and boarding interval, now they are in minutes
    cols = ['ED_Admit_ICU', 'ED_Admit_MED_SURG_TELE', 'ED_Admit_NICU', 'ED_Admit_Peds',
            'ED_Admit_PICU', 'ED_Admit_WMN_PAV', 'ED_Admit_Obstetrics', 'ED_Admit_IP_Surge']


    # sum available admit columns (skip missing)
    admit_cols = [c for c in cols if c in df.columns]
    df['total_adm_from_ED'] = df[admit_cols].sum(axis=1).fillna(0)
    df['stepdown_to_ward'] = 0.42 * df['OCC_BEDS_IP_SURGE'].mean()

    cols = ['Date',"AVERAGE_ED_WAITING_INTERVAL", "AVERAGE_ED_BOARDING_INTERVAL",
            'AVERAGE_ED_LOS_INTERVAL', 'DAILY_ED_ARRIVALS', 'DAILY_LWBT_COUNT',
            'ED_Admit_ICU', 'ED_Admit_MED_SURG_TELE', 'ED_Admit_IP_Surge',  'ED_Admit_NICU', 'ED_Admit_Peds',
            'ED_Admit_PICU', 'ED_Admit_WMN_PAV', 'ED_Admit_Obstetrics',
            'total_adm_from_ED', 'DIRECT_Admt_IP_Surge','DIRECT_Admt_MED_SURG_TELE','DIRECT_Admt_ICU',
            'TRNSFR_ADMT_IP_Surge', 'TRNSFR_ADMT_MED_SURG_TELE','TRNSFR_ADMT_ICU', 'stepdown_to_ward',
            'IP_Surge_TO_ICU', 'MED_SURG_TELE_TO_ICU', 'ICU_TO_IP_Surge',
            'ICU_TO_MED_SURG_TELE', 'Discharges_IP_Surge', 'Discharges_MED_SURG_TELE', 'Discharges_ICU', 'OCC_BEDS_IP_SURGE',
            'OCC_BEDS_MED_SURG_TELE', 'OCC_BEDS_ICU']
    df = df[cols]
    return df


# =============================================================================
# PART 2: CREATE EXAMPLE DATASET FOR THE APP
# =============================================================================

df = procces_data('2024-01-01')
print(f"Data loaded: {len(df)} days from {df['Date'].min()} to {df['Date'].max()}")
df_renamed = df.rename(columns={"AVERAGE_ED_WAITING_INTERVAL": 'avg_ED_wait_time',
                                'AVERAGE_ED_BOARDING_INTERVAL': 'avg_ED_boarding_time',
                                'AVERAGE_ED_LOS_INTERVAL':'avg_ED_length_of_stay',
                                'DAILY_ED_ARRIVALS':'daily_ED_arrivals',
                                'DAILY_LWBT_COUNT':'left_without_being_seen',
                                'ED_Admit_ICU':'ED_to_ICU_admissions',
                                'ED_Admit_MED_SURG_TELE':'ED_to_ward_admissions',
                                'ED_Admit_IP_Surge':'ED_to_stepdown_admissions',

                                'OCC_BEDS_MED_SURG_TELE':'ward_occupied_beds',
                                'Discharges_MED_SURG_TELE':'ward_discharges',
                                'DIRECT_Admt_MED_SURG_TELE':'ward_direct_admission',
                                'TRNSFR_ADMT_MED_SURG_TELE':'ward_transfer_admission',
                                'MED_SURG_TELE_TO_ICU': 'ward_to_ICU',

                                'OCC_BEDS_IP_SURGE':'stepdown_occupied_beds',
                                'Discharges_IP_Surge':'stepdown_discharges',
                                'DIRECT_Admt_IP_Surge':'stepdown_direct_admission',
                                'TRNSFR_ADMT_IP_Surge':'stepdown_transfer_admission',
                                'IP_Surge_TO_ICU':'stepdown_to_ICU',

                                'OCC_BEDS_ICU':'ICU_occupied_beds',
                                'Discharges_ICU':'ICU_discharges',
                                'DIRECT_Admt_ICU':'ICU_direct_admission',
                                'TRNSFR_ADMT_ICU':'ICU_transfer_admission',
                                'ICU_TO_IP_Surge':'ICU_to_stepdown',
                                'ICU_TO_MED_SURG_TELE':'ICU_to_ward'})

# Save example dataset for app upload
# Uncomment to save:
# df_renamed.to_excel("data/data_example.xlsx", index=False)
print("\n✅ Example dataset ready for app upload")
print("   (Uncomment the to_excel line to save)")

# =============================================================================
# PART 3: DEFAULT PARAMETERS FOR MANUAL ENTRY
# =============================================================================

print("\n" + "=" * 60)
print("DEFAULT PARAMETERS FOR MANUAL ENTRY")
print("=" * 60)
"""
These values are calculated from the dataset and used as defaults in the app.
They represent mean values from the period 2024-01-01 to 2025-03-31.
"""

default_values = {
    # ED metrics
    'avg_ED_wait_time': df_renamed['avg_ED_wait_time'].mean(),
    'avg_ED_boarding_time': df_renamed['avg_ED_boarding_time'].mean(),
    'avg_ED_length_of_stay': df_renamed['avg_ED_length_of_stay'].mean(),
    'daily_ED_arrivals': df_renamed['daily_ED_arrivals'].mean(),
    'left_without_being_seen': df_renamed['left_without_being_seen'].mean(),

    # ED admissions
    'ED_to_ICU_admissions': df_renamed['ED_to_ICU_admissions'].mean(),
    'ED_to_ward_admissions': df_renamed['ED_to_ward_admissions'].mean(),
    'ED_to_stepdown_admissions': df_renamed['ED_to_stepdown_admissions'].mean(),
    'total_adm_from_ED': df_renamed['total_adm_from_ED'].mean(),

    # ICU metrics
    'ICU_direct_admission': df_renamed.loc[df_renamed['ICU_direct_admission'] != 0, 'ICU_direct_admission'].median(),
    'ICU_discharges': df_renamed['ICU_discharges'].mean(),
    'ICU_transfer_admission': df_renamed['ICU_transfer_admission'].mean(),
    'ICU_occupied_beds': df_renamed['ICU_occupied_beds'].mean(),
    'ICU_to_stepdown': df_renamed['ICU_to_stepdown'].mean(),
    'ICU_to_ward': df_renamed['ICU_to_ward'].mean(),

    # Ward metrics
    'ward_direct_admission': df_renamed['ward_direct_admission'].mean(),
    'ward_transfer_admission': df_renamed['ward_transfer_admission'].mean(),
    'ward_occupied_beds': df_renamed['ward_occupied_beds'].mean(),
    'ward_discharges': df_renamed['ward_discharges'].mean(),
    'ward_to_ICU': df_renamed['ward_to_ICU'].mean(),

    # Step-down metrics
    'stepdown_direct_admission': df_renamed['stepdown_direct_admission'].mean(),
    'stepdown_discharges': df_renamed['stepdown_discharges'].mean(),
    'stepdown_to_ward': df_renamed['stepdown_to_ward'].mean(),
    'stepdown_to_ICU': df_renamed['stepdown_to_ICU'].mean(),
    'stepdown_transfer_admission': df_renamed['stepdown_transfer_admission'].mean(),
    'stepdown_occupied_beds': df_renamed['stepdown_occupied_beds'].mean(),
}

# print("\nDefault values for manual entry:")
# for key, value in default_values.items():
#     print(f"{key:30} = {value:10.2f}")

"""
Default values for manual entry:
avg_ED_wait_time               =     112.59
avg_ED_boarding_time           =     973.73
avg_ED_length_of_stay          =     456.34
daily_ED_arrivals              =     270.83
left_without_being_seen        =       7.16
ED_to_ICU_admissions           =       6.59
ED_to_ward_admissions          =      35.04
ED_to_stepdown_admissions      =       1.44
total_adm_from_ED              =      50.03
ICU_direct_admission           =       2.00
ICU_discharges                 =       3.05
ICU_transfer_admission         =       3.37
ICU_occupied_beds              =      76.95
ICU_to_stepdown                =       0.10
ICU_to_ward                    =      12.80
ward_direct_admission          =       9.28
ward_transfer_admission        =       7.64
ward_occupied_beds             =     400.34
ward_discharges                =      66.38
ward_to_ICU                    =       2.98
stepdown_direct_admission      =       5.28
stepdown_discharges            =       2.34
stepdown_to_ward               =       3.53
stepdown_to_ICU                =       0.78
stepdown_transfer_admission    =       0.60
stepdown_occupied_beds         =       8.39
"""

# =============================================================================
# PART 4: VALIDATION - Compute parameters using independent function
# =============================================================================

print("\n" + "=" * 60)
print("VALIDATION: PARAMETER CALCULATION")
print("=" * 60)

def compute_params_from_df(df):
    """
    INDEPENDENT parameter calculation function.
    This uses the original column names and serves as a validation reference.
    The app should produce identical results when using the renamed columns.
    """

    params={}
    MIN2DAY = 1.0 / 1440.0
    mean_wait_min = float(df['AVERAGE_ED_WAITING_INTERVAL'].dropna().mean())
    mean_board_min = float(df['AVERAGE_ED_BOARDING_INTERVAL'].dropna().mean())
    mean_LOS_days = float(df['AVERAGE_ED_LOS_INTERVAL'].dropna().mean()) * MIN2DAY

    mean_wait_days = max(mean_wait_min * MIN2DAY, 1e-6)
    mean_board_days = max(mean_board_min * MIN2DAY, 1e-6)

    params["sigma"] = 1.0 / mean_wait_days  # rate to be attended (per day)
    psi = 1.0 / mean_board_days  # boarding -> inpatient transfer rate

    # LWBT fraction and omega
    total_arr = df['DAILY_ED_ARRIVALS'].sum()
    total_lwbt = df['DAILY_LWBT_COUNT'].sum() if 'DAILY_LWBT_COUNT' in df.columns else 0.0
    f = float(total_lwbt) / total_arr if total_arr > 0 else 0.0
    f = np.clip(f, 0.0, 0.9999)
    params["omega"]  = params["sigma"] * f / max((1.0 - f), 1e-9)

    # p_admit: if admitted series available compute fraction among seen
    cols = ['ED_Admit_ICU', 'ED_Admit_MED_SURG_TELE', 'ED_Admit_NICU', 'ED_Admit_Peds',
        'ED_Admit_PICU', 'ED_Admit_WMN_PAV', 'ED_Admit_Obstetrics', 'ED_Admit_IP_Surge']
    # sum available admit columns (skip missing)
    admit_cols = [c for c in cols if c in df.columns]
    total_adm_from_ED = df[admit_cols].sum(axis=1).fillna(0)
    total_adm = total_adm_from_ED.sum()

    seen_total = total_arr - total_lwbt
    if seen_total <= 0:
        p_admit = 0.15  # fallback
    else:
        p_admit = total_adm / seen_total

    params["pED_to_step"] = df['ED_Admit_IP_Surge'].sum() / seen_total
    params["pED_to_ward"] = df['ED_Admit_MED_SURG_TELE'].sum() / seen_total
    params["pED_to_ICU"] = df['ED_Admit_ICU'].sum() / seen_total

    mean_service = mean_LOS_days - mean_wait_days - p_admit * mean_board_days
    params["gamma"] = 1.0 / mean_service

    mean_board_Hs = mean_board_days
    mean_board_ICU = mean_board_days* 1  # 0.7
    mean_board_Hm = mean_board_days * 1  #

    params["xi_ICU"] = 1.0 / max(mean_board_ICU, 1e-6)
    params["xi_ward"] = 1.0 / max(mean_board_Hm, 1e-6)
    params["xi_step"] = 1.0 / max(mean_board_Hs, 1e-6)


    # varphi_Hm = 0.42 # stepdown to ward

    params["step_to_ICU_rate"] = df['IP_Surge_TO_ICU'].sum() / df['OCC_BEDS_IP_SURGE'].sum() # varphi_I
    params["step_discharge_rate"] = df['Discharges_IP_Surge'].sum() / df['OCC_BEDS_IP_SURGE'].sum() # varphi_D
    params["step_to_ward_rate"] = 0.42 # stepdown to ward #---- varphi_Hm

    params["ward_to_ICU_rate"] = df['MED_SURG_TELE_TO_ICU'].sum() / df['OCC_BEDS_MED_SURG_TELE'].sum()
    #psi_I = df['MED_SURG_TELE_TO_ICU'].sum() / df['OCC_BEDS_MED_SURG_TELE'].sum()


    #psi_D = df['Discharges_MED_SURG_TELE'].sum() / df['OCC_BEDS_MED_SURG_TELE'].sum()
    params["ward_discharge_rate"] = df['Discharges_MED_SURG_TELE'].sum() / df['OCC_BEDS_MED_SURG_TELE'].sum()
    params["ICU_to_step_rate"] = df['ICU_TO_IP_Surge'].sum() / df['OCC_BEDS_ICU'].sum() # eps_Hs
    params["ICU_to_ward_rate"] = df['ICU_TO_MED_SURG_TELE'].sum() / df['OCC_BEDS_ICU'].sum() #eps_Hm
    params["ICU_discharge_rate"] = df['Discharges_ICU'].sum() / df['OCC_BEDS_ICU'].sum() # eps_D



    params_formatted = {'sigma': params["sigma"] , 'omega': params["omega"] , 'psi': psi,  'gamma': params["gamma"],
            'f_lwbt': f, 'mean_wait_days': mean_wait_days, 'mean_board_days': mean_board_days,
            'pED_Hs':params["pED_to_step"], 'pED_Hm':params["pED_to_ward"], 'pED_ICU':params["pED_to_ICU"],
            'xi_I':params["xi_ICU"], 'xi_Hm': params["xi_ward"], 'xi_Hs': params["xi_step"],
            'varphi_I':params["step_to_ICU_rate"] , 'varphi_D':params["step_discharge_rate"],
            'varphi_Hm':params["step_to_ward_rate"], 'psi_I':params["ward_to_ICU_rate"],
            'psi_D':params["ward_discharge_rate"],
            'eps_Hs':params["ICU_to_step_rate"], 'eps_Hm':params["ICU_to_ward_rate"], 'eps_D':params["ICU_discharge_rate"]}

    return params, params_formatted

# Compute parameters for validation
params, fixed_params=compute_params_from_df(df)
# print("\nComputed Parameters (Validation Reference):")
# print(params)

"""
{'sigma': 12.78927994079037,
 'omega': 0.3470850212651911,
 'pED_to_step': 0.005464344528170069,
 'pED_to_ward': 0.1329074970474242,
 'pED_to_ICU': 0.024976296222366384,
 'gamma': 9.056719486295984,
 'xi_ICU': 1.4788523039502726,
 'xi_ward': 1.4788523039502726,
 'xi_step': 1.4788523039502726,
 'step_to_ICU_rate': 0.09299895506792058,
 'step_discharge_rate': 0.27873563218390807,
 'step_to_ward_rate': 0.42,
 'ward_to_ICU_rate': 0.0074498912644547065,
 'ward_discharge_rate': 0.165809381385132,
 'ICU_to_step_rate': 0.0013109895120839033,
 'ICU_to_ward_rate': 0.16638166894664844,
 'ICU_discharge_rate': 0.03964318285453716}
"""


# =============================================================================
# PART 5: VALIDATION - Compute equilibrium using independent function
# =============================================================================
print("\n" + "=" * 60)
print("VALIDATION: EQUILIBRIUM CALCULATION")
print("=" * 60)

def compute_equilibrium_data(fixed_params, arrivals_mean, Ad_Hs_mean, Ad_Hm_mean, Ad_ICU_mean,
                             At_Hs_mean, At_Hm_mean, At_ICU_mean):
    sigma = fixed_params['sigma']
    omega = fixed_params['omega']

    pED_Hs = fixed_params['pED_Hs']
    pED_Hm = fixed_params['pED_Hm']
    pED_ICU = fixed_params['pED_ICU']

    xi_I = fixed_params['xi_I']
    xi_Hs = fixed_params['xi_Hs']
    xi_Hm = fixed_params['xi_Hm']

    varphi_I = fixed_params['varphi_I']
    varphi_D = fixed_params['varphi_D'] #0.25
    varphi_Hm = fixed_params['varphi_Hm']
    eps_Hs = fixed_params['eps_Hs']

    ###############################
    gamma = fixed_params['gamma']
    eps_Hm = fixed_params['eps_Hm']
    psi_D = fixed_params['psi_D']
    psi_I = fixed_params['psi_I']
    eps_D = fixed_params['eps_D']

    # Step 2a: upstream compartments
    W_star = arrivals_mean / (sigma + omega)
    S_star = sigma * W_star / gamma

    B_Hs_star = pED_Hs * gamma * S_star / xi_Hs
    B_Hm_star = pED_Hm * gamma * S_star / xi_Hm
    B_I_star = pED_ICU * gamma * S_star / xi_I

    # Step 2b: total admissions including external and internal
    A_Hs = xi_Hs * B_Hs_star + Ad_Hs_mean + At_Hs_mean
    A_Hm = xi_Hm * B_Hm_star + Ad_Hm_mean + At_Hm_mean
    A_I = xi_I * B_I_star + Ad_ICU_mean + At_ICU_mean

    A_mat = np.array([[varphi_I + varphi_D + varphi_Hm, 0, -eps_Hs],
        [-varphi_Hm, psi_I + psi_D, -eps_Hm],
        [-varphi_I, -psi_I, eps_Hs + eps_Hm + eps_D]])
    b_vec = np.array([A_Hs, A_Hm, A_I])
    Hs_star, Hm_star, I_star = np.linalg.solve(A_mat, b_vec)
    D_star = varphi_D * Hs_star + psi_D * Hm_star + eps_D * I_star

    return { "W": W_star, "S": S_star, "B_Hs": B_Hs_star, "B_Hm": B_Hm_star,  "B_I": B_I_star, "Hs": Hs_star,
             "Hm": Hm_star,  "I": I_star, "D": D_star }


Ad_Hs = df['DIRECT_Admt_IP_Surge'].values
Ad_Hm = df['DIRECT_Admt_MED_SURG_TELE'].values
Ad_ICU = df['DIRECT_Admt_ICU'].values

At_Hs = df['TRNSFR_ADMT_IP_Surge'].values
At_Hm = df['TRNSFR_ADMT_MED_SURG_TELE'].values
At_ICU = df['TRNSFR_ADMT_ICU'].values


arrivals = df['DAILY_ED_ARRIVALS'].values
# Calculate means (with special handling for ICU direct admits)
arrivals_mean = arrivals.mean()
Ad_Hs_mean = Ad_Hs.mean()
Ad_Hm_mean = Ad_Hm.mean()
Ad_ICU_mean = np.nanmedian(Ad_ICU[Ad_ICU != 0]) # Use median to avoid zero inflation
At_Hs_mean = At_Hs.mean()
At_Hm_mean = At_Hm.mean()
At_ICU_mean = At_ICU.mean()

df = procces_data('2024-01-01')

results= compute_equilibrium_data(fixed_params, arrivals_mean, Ad_Hs_mean, Ad_Hm_mean, Ad_ICU_mean,
                             At_Hs_mean, At_Hm_mean, At_ICU_mean)

# print("\nEquilibrium Results (Validation Reference):")
# print("{")
# for key, value in results.items():
#     print(f"  '{key}': {value:14.10f},")
# print("}")

"""
Equilibrium Results (Validation Reference):
{
  'W':  20.6165674575,
  'S':  29.1133067587,
  'B_Hs':   0.9742619123,
  'B_Hm':  23.6966596025,
  'B_I':   4.4531332157,
  'Hs':   9.3745210034,
  'Hm': 395.6775485148,
  'I':  76.0983176049,
  'D':  71.2368421053,
}
"""


# =============================================================================
# PART 6: VALIDATION CHECKLIST
# =============================================================================

print("\n" + "=" * 60)
print("VALIDATION CHECKLIST")
print("=" * 60)

print("""
When testing the app, verify that:

1. PARAMETER CALCULATION:
   - Upload 'data_example.xlsx' to the app
   - Compare computed parameters with the validation values above
   - All values should match within small floating-point误差

2. EQUILIBRIUM CALCULATION:
   - After uploading data, click "Calculate Equilibrium"
   - Compare results with validation values above
   - Patient counts should match closely

3. DEFAULT VALUES:
   - Switch to "Manual entry" mode
   - Verify default values match those shown in PART 3
   - Values should be pre-filled correctly

4. COLUMN MAPPING:
   - The app expects column names matching df_renamed
   - Original data uses different names (mapped in PART 2)
   - Ensure no columns are lost in the mapping
""")

print("\n✅ Validation script complete!")
print("   Use these reference values to verify app functionality.")