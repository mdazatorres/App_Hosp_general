import numpy as np
import pandas as pd



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
    df["AVERAGE_ED_WAITING_INTERVAL_DAYS"] = df["AVERAGE_ED_WAITING_INTERVAL"] / 1440
    df["AVERAGE_ED_BOARDING_INTERVAL_DAYS"] = df["AVERAGE_ED_BOARDING_INTERVAL"] / 1440

    df['AVERAGE_ED_WAITING_INTERVAL_DAYS'] = df["AVERAGE_ED_WAITING_INTERVAL"] / 1440
    df['AVERAGE_ED_BOARDING_INTERVAL_DAYS'] = df["AVERAGE_ED_BOARDING_INTERVAL"] / 1440
    df['AVERAGE_ED_LOS_INTERVAL_DAYS'] = df["AVERAGE_ED_LOS_INTERVAL"] / 1440
    cols = ['ED_Admit_ICU', 'ED_Admit_MED_SURG_TELE', 'ED_Admit_NICU', 'ED_Admit_Peds',
            'ED_Admit_PICU', 'ED_Admit_WMN_PAV', 'ED_Admit_Obstetrics', 'ED_Admit_IP_Surge']
    # sum available admit columns (skip missing)
    admit_cols = [c for c in cols if c in df.columns]
    df['total_adm_from_ED'] = df[admit_cols].sum(axis=1).fillna(0)
    df['stepdown_to_ward'] = 0.42 * df['OCC_BEDS_IP_SURGE'].mean()

    cols = ['Date',"AVERAGE_ED_WAITING_INTERVAL_DAYS", "AVERAGE_ED_BOARDING_INTERVAL",
               'AVERAGE_ED_LOS_INTERVAL', 'DAILY_ED_ARRIVALS', 'DAILY_LWBT_COUNT', 'ED_Admit_ICU',
               'ED_Admit_MED_SURG_TELE', 'ED_Admit_IP_Surge','total_adm_from_ED', 'DIRECT_Admt_IP_Surge',
               'DIRECT_Admt_MED_SURG_TELE','DIRECT_Admt_ICU', 'TRNSFR_ADMT_IP_Surge', 'TRNSFR_ADMT_MED_SURG_TELE',
               'TRNSFR_ADMT_ICU', 'stepdown_to_ward', 'IP_Surge_TO_ICU', 'MED_SURG_TELE_TO_ICU', 'ICU_TO_IP_Surge',
               'ICU_TO_MED_SURG_TELE', 'Discharges_IP_Surge', 'Discharges_MED_SURG_TELE', 'Discharges_ICU', 'OCC_BEDS_IP_SURGE',
               'OCC_BEDS_MED_SURG_TELE', 'OCC_BEDS_ICU']
    df= df[cols]


    return df


#varphi_Hm = 0.42
df = procces_data()


df_renamed = df.rename(columns={"AVERAGE_ED_WAITING_INTERVAL_DAYS": 'avg_ED_wait_time',
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

df_renamed.to_excel("data/data_example.xlsx", index=False)

