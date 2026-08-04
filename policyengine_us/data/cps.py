import numpy as np


CPS_FLSA_NEVER_WORKED_OCCUPATION_CODE = 53
CPS_FLSA_MILITARY_OCCUPATION_CODE = 52
CPS_FLSA_COMPUTER_SCIENTIST_OCCUPATION_CODE = 8
CPS_FLSA_FARMER_FISHER_OCCUPATION_CODE = 41

CPS_FLSA_EXECUTIVE_ADMINISTRATIVE_PROFESSIONAL_OCCUPATION_CODES = np.array(
    [
        1,  # Chief executives, and managers
        2,  # Compensation, human resources, and infrastructure managers
        3,  # All other managers
        5,  # Business operations specialists
        6,  # Accountants and auditors
        7,  # Financial specialists
        9,  # Mathematical science occupations
        10,  # Architects, except naval
        11,  # Surveyors, cartographers, & photogrammetrists
        12,  # Engineering technologists and technicians
        13,  # Earth scientists
        14,  # Economists
        15,  # Psychologists, and other social scientists
        16,  # Health and safety specialists
        18,  # Lawyers, judges, magistrates, and other judicial workers
        19,  # Paralegals and all other legal support workers
        25,  # Registered nurses, therapists, and specific pathologists
        26,  # Veterinarians
        27,  # Health technicians and other healthcare practitioners
        28,  # Healthcare support occupations
        29,  # First-line supervisors of protective service workers
        34,  # First-line supervisors of housekeeping and janitorial workers
        36,  # Supervisors of personal care and service workers
        38,  # First-line supervisors of retail/non-retail sales workers
        39,  # Sales and related occupations
        40,  # Office & administrative support occupations
        42,  # First-line supervisors of construction trades workers
        50,  # Supervisors of transportation and flight related workers
    ],
    dtype=np.int16,
)

CPS_FLSA_OVERTIME_OCCUPATION_CODES = {
    "has_never_worked": CPS_FLSA_NEVER_WORKED_OCCUPATION_CODE,
    "is_military": CPS_FLSA_MILITARY_OCCUPATION_CODE,
    "is_computer_scientist": CPS_FLSA_COMPUTER_SCIENTIST_OCCUPATION_CODE,
    "is_farmer_fisher": CPS_FLSA_FARMER_FISHER_OCCUPATION_CODE,
}
