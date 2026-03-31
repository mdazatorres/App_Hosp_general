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

BASE_DATA_MANUAL = {
    "ED": ["daily_ED_arrivals", "left_without_being_seen", "avg_ED_wait_time",
           "avg_ED_boarding_time", "avg_ED_treatment_time",  "total_adm_from_ED"],
    "WARD": ["ward_occupied_beds", "ward_discharges", "ward_direct_admission",
             "ward_transfer_admission", "ward_to_ICU"],
    "STEP": ["stepdown_occupied_beds", "stepdown_discharges", "stepdown_direct_admission",
             "stepdown_transfer_admission", "stepdown_to_ICU", "stepdown_to_ward"],
    "ICU": ["ICU_occupied_beds", "ICU_discharges", "ICU_direct_admission",
            "ICU_transfer_admission", 'ICU_to_stepdown', 'ICU_to_ward']
}

# I think I just need one dictionary

# Data dictionary with explanations
DATA_DICTIONARY = {
    # ED variables
    'daily_ED_arrivals': {
        'name': 'Avg ED Arrivals',
        'description': 'Average number of patients arriving to the Emergency Department per day',
        'unit': 'patients/day',
        'category': 'ED'
    },
    'left_without_being_seen': {
        'name': 'Left Without Being Seen',
        'description': 'Average number of patients who leave without being seen per day',
        'unit': 'patients/day',
        'category': 'ED'
    },
    'avg_ED_wait_time': {
        'name': 'Avg ED Wait Time',
        'description': 'Average time patients wait before receiving initial treatment',
        'unit': 'minutes',
        'category': 'ED'
    },
    'avg_ED_boarding_time': {
        'name': 'Avg ED Boarding Time',
        'description': 'Average time admitted patients wait for an inpatient bed',
        'unit': 'minutes',
        'category': 'ED'
    },
    'avg_ED_treatment_time': {
        'name': 'Avg ED Treatment Time',
        'description': 'Average treatment time in the ED',
        'unit': 'minutes',
        'category': 'ED'
    },
    'total_adm_from_ED': {
        'name': 'Avg Admissions to ICU',
        'description': 'Average number of patients admitted to the hospital from ED per day',
        'unit': 'patients/day',
        'category': 'ED'
    },
    'ED_to_ward_admissions': {
        'name': 'ED Admissions to Ward',
        'description': 'Average number of ED patients admitted to General Ward per day',
        'unit': 'patients/day',
        'category': 'ED'
    },
    'ED_to_stepdown_admissions': {
        'name': 'ED Admissions to Stepdown',
        'description': 'Average number of ED patients admitted to Step-down unit per day',
        'unit': 'patients/day',
        'category': 'ED'
    },
    'ED_to_ICU_admissions': {
        'name': 'ED Admissions to ICU',
        'description': 'Average number of ED patients admitted to ICU per day',
        'unit': 'patients/day',
        'category': 'ED'
    },

    # WARD variables
    'ward_occupied_beds': {
        'name': 'Avg Ward Occupied Beds',
        'description': 'Average daily number of occupied beds in the General Ward',
        'unit': 'beds',
        'category': 'WARD'
    },
    'ward_discharges': {
        'name': 'Avg Ward Discharges',
        'description': 'Average number of patients discharged from General Ward per day',
        'unit': 'patients/day',
        'category': 'WARD'
    },
    'ward_direct_admission': {
        'name': 'Avg Ward Direct Admission',
        'description': 'Average number of patients directly admitted to General Ward (non-ED) per day',
        'unit': 'patients/day',
        'category': 'WARD'
    },
    'ward_transfer_admission': {
        'name': 'Avg Ward Transfer Admission',
        'description': 'Average number of patients transferred into General Ward from other units per day',
        'unit': 'patients/day',
        'category': 'WARD'
    },
    'ward_to_ICU': {
        'name': 'Avg Ward to ICU Transfers',
        'description': 'Average number of patients transferred from General Ward to ICU per day',
        'unit': 'patients/day',
        'category': 'WARD'
    },

    # STEP-DOWN variables
    'stepdown_occupied_beds': {
        'name': 'Avg StepDown Occupied Beds',
        'description': 'Average daily number of occupied beds in the Step-down unit',
        'unit': 'beds',
        'category': 'STEP'
    },
    'stepdown_discharges': {
        'name': 'Avg StepDown Discharges',
        'description': 'Average number of patients discharged from Step-down unit per day',
        'unit': 'patients/day',
        'category': 'STEP'
    },
    'stepdown_direct_admission': {
        'name': 'Avg StepDown Direct Admission',
        'description': 'Average number of patients directly admitted to Step-down unit (non-ED) per day',
        'unit': 'patients/day',
        'category': 'STEP'
    },
    'stepdown_transfer_admission': {
        'name': 'Avg StepDown Transfer Admission',
        'description': 'Average number of patients transferred into Step-down unit from other units per day',
        'unit': 'patients/day',
        'category': 'STEP'
    },
    'stepdown_to_ICU': {
        'name': 'Avg StepDown to ICU Transfers',
        'description': 'Average number of patients transferred from Step-down to ICU per day',
        'unit': 'patients/day',
        'category': 'STEP'
    },
    'stepdown_to_ward': {
        'name': 'Avg StepDown to Ward Transfers',
        'description': 'Average number of patients transferred from Step-down to General Ward per day',
        'unit': 'patients/day',
        'category': 'STEP'
    },

    # ICU variables
    'ICU_occupied_beds': {
        'name': 'Avg ICU Occupied Beds',
        'description': 'Average daily number of occupied beds in the ICU',
        'unit': 'beds',
        'category': 'ICU'
    },
    'ICU_discharges': {
        'name': 'Avg ICU Discharges',
        'description': 'Average number of patients discharged from ICU per day',
        'unit': 'patients/day',
        'category': 'ICU'
    },
    'ICU_direct_admission': {
        'name': 'Avg ICU Direct Admission',
        'description': 'Average number of patients directly admitted to ICU (non-ED) per day',
        'unit': 'patients/day',
        'category': 'ICU'
    },
    'ICU_transfer_admission': {
        'name': 'Avg ICU Transfer Admission',
        'description': 'Average number of patients transferred into ICU from other units per day',
        'unit': 'patients/day',
        'category': 'ICU'
    },
    'ICU_to_stepdown': {
        'name': 'Avg ICU to Stepdown Transfers',
        'description': 'Average number of patients transferred from ICU to Step-down per day',
        'unit': 'patients/day',
        'category': 'ICU'
    },
    'ICU_to_ward': {
        'name': 'Avg ICU to Ward Transfers',
        'description': 'Average number of patients transferred from ICU to General Ward per day',
        'unit': 'patients/day',
        'category': 'ICU'
    }
}

#
#
#
# MANUAL_DATA_DICTIONARY = {
#     # ED variables
#     'daily_ED_arrivals': {
#         'description': 'Average number of patients arriving to the Emergency Department per day',
#         'unit': 'patients/day',
#         'category': 'ED'
#     },
#     'left_without_being_seen': {
#         'description': 'Average number of patients who leave without being seen per day',
#         'unit': 'patients/day',
#         'category': 'ED'
#     },
#     'avg_ED_wait_time': {
#         'description': 'Average time patients wait before receiving initial treatment',
#         'unit': 'minutes',
#         'category': 'ED'
#     },
#     'avg_ED_treatment_time': {
#         'description': 'Average treatment time in the ED',
#         'unit': 'hours',
#         'category': 'ED'
#     },
#     'avg_ED_boarding_time': {
#         'description': 'Average time admitted patients wait for an inpatient bed',
#         'unit': 'minutes',
#         'category': 'ED'
#     },
#     'total_adm_from_ED': {
#         'description': 'Average number of patients admitted to the hospital from ED per day',
#         'unit': 'patients/day',
#         'category': 'ED'
#     },
#     'ED_to_ward_admissions': {
#         'description': 'Average number of ED patients admitted to General Ward per day',
#         'unit': 'patients/day',
#         'category': 'ED'
#     },
#     'ED_to_stepdown_admissions': {
#         'description': 'Average number of ED patients admitted to Step-down unit per day',
#         'unit': 'patients/day',
#         'category': 'ED'
#     },
#     'ED_to_ICU_admissions': {
#         'description': 'Average number of ED patients admitted to ICU per day',
#         'unit': 'patients/day',
#         'category': 'ED'
#     },
#
#     # WARD variables
#     'ward_occupied_beds': {
#         'description': 'Average daily number of occupied beds in the General Ward',
#         'unit': 'beds',
#         'category': 'WARD'
#     },
#     'ward_discharges': {
#         'description': 'Average number of patients discharged from General Ward per day',
#         'unit': 'patients/day',
#         'category': 'WARD'
#     },
#     'ward_direct_admission': {
#         'description': 'Average number of patients directly admitted to General Ward (non-ED) per day',
#         'unit': 'patients/day',
#         'category': 'WARD'
#     },
#     'ward_transfer_admission': {
#         'description': 'Average number of patients transferred into General Ward from other units per day',
#         'unit': 'patients/day',
#         'category': 'WARD'
#     },
#     'ward_to_ICU': {
#         'description': 'Average number of patients transferred from General Ward to ICU per day',
#         'unit': 'patients/day',
#         'category': 'WARD'
#     },
#
#     # STEP-DOWN variables
#     'stepdown_occupied_beds': {
#         'description': 'Average daily number of occupied beds in the Step-down unit',
#         'unit': 'beds',
#         'category': 'STEP'
#     },
#     'stepdown_discharges': {
#         'description': 'Average number of patients discharged from Step-down unit per day',
#         'unit': 'patients/day',
#         'category': 'STEP'
#     },
#     'stepdown_direct_admission': {
#         'description': 'Average number of patients directly admitted to Step-down unit (non-ED) per day',
#         'unit': 'patients/day',
#         'category': 'STEP'
#     },
#     'stepdown_transfer_admission': {
#         'description': 'Average number of patients transferred into Step-down unit from other units per day',
#         'unit': 'patients/day',
#         'category': 'STEP'
#     },
#     'stepdown_to_ICU': {
#         'description': 'Average number of patients transferred from Step-down to ICU per day',
#         'unit': 'patients/day',
#         'category': 'STEP'
#     },
#     'stepdown_to_ward': {
#         'description': 'Average number of patients transferred from Step-down to General Ward per day',
#         'unit': 'patients/day',
#         'category': 'STEP'
#     },
#
#     # ICU variables
#     'ICU_occupied_beds': {
#         'description': 'Average daily number of occupied beds in the ICU',
#         'unit': 'beds',
#         'category': 'ICU'
#     },
#     'ICU_discharges': {
#         'description': 'Average number of patients discharged from ICU per day',
#         'unit': 'patients/day',
#         'category': 'ICU'
#     },
#     'ICU_direct_admission': {
#         'description': 'Average number of patients directly admitted to ICU (non-ED) per day',
#         'unit': 'patients/day',
#         'category': 'ICU'
#     },
#     'ICU_transfer_admission': {
#         'description': 'Average number of patients transferred into ICU from other units per day',
#         'unit': 'patients/day',
#         'category': 'ICU'
#     },
#     'ICU_to_stepdown': {
#         'description': 'Average number of patients transferred from ICU to Step-down per day',
#         'unit': 'patients/day',
#         'category': 'ICU'
#     },
#     'ICU_to_ward': {
#         'description': 'Average number of patients transferred from ICU to General Ward per day',
#         'unit': 'patients/day',
#         'category': 'ICU'
#     }
# }
#########
# data/excel_dictionary.py




# Default values for all parameters
DEFAULT_VALUES = {
        # ED defaults
        'daily_ED_arrivals': 270.82,
        'left_without_being_seen': 7.15,
        'avg_ED_wait_time': 112.59,
        'avg_ED_boarding_time': 973.72,
        'avg_ED_length_of_stay': 456.33,
        "avg_ED_treatment_time": 1440*(1/9.056),  # check this
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

# default_params_ = {
#     # ED parameters
#     'daily_ED_arrivals_avg': 270.82,
#     'sigma': 12.78,
#     'omega': 0.34,
#     'gamma': 9.056,
#     'pED_to_step': 0.005464344528170069,
#     'pED_to_ward': 0.1329074970474242,
#     'pED_to_ICU': 0.024976296222366384,
#     'xi_ICU': 1.4788523039502726,
#     'xi_ward': 1.4788523039502726,
#     'xi_step': 1.4788523039502726,
#
#     # Ward parameters
#     'ward_discharge_rate': 0.165809381385132,
#     'ward_to_ICU_rate': 0.0074498912644547065,
#     'ward_direct_admission_avg': 9.28,
#     'ward_transfer_admission_avg': 7.64,
#
#     # Step-down parameters
#     'step_discharge_rate': 0.27873563218390807,
#     'step_to_ICU_rate': 0.09299895506792058,
#     'step_to_ward_rate': 0.42,
#     'stepdown_direct_admission_avg': 5.28,
#     'stepdown_transfer_admission_avg': 0.60,
#
#     # ICU parameters
#     'ICU_discharge_rate': 0.03964318285453716,
#     'ICU_to_ward_rate': 0.16638166894664844,
#     'ICU_to_step_rate': 0.0013109895120839033,
#     'ICU_direct_admission_avg': 2.00,
#     'ICU_transfer_admission_avg': 3.37,
# }


