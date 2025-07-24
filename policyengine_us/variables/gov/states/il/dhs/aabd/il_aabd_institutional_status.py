from policyengine_us.model_api import *


class IllinoisAABDInstitutionalStatus(Enum):
    A = "A"  # Public Institution (Ineligible)
    B = "B"  # Institution for Mental Diseases (IMD) Ages 22-64 (Ineligible)
    C = "C"  # Public Educational/Vocational Training Institution (MANG Only)
    D = "D"  # Correctional/Penal Institution (Ineligible)
    E = "E"  # Certified Private Psychiatric Hospital (Age 65+)
    F = "F"  # Accredited Private Psychiatric Hospital (Under Age 21)
    G = "G"  # Private Institution (Life Care Contract, Ineligible)
    H = "H"  # Private Institution (Prepaid Care Not Consumed, Ineligible)
    I = "I"  # Non-Compliant Facility (Ineligible)
    NONE = "None"


class il_aabd_institutional_status(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = IllinoisAABDInstitutionalStatus
    default_value = IllinoisAABDInstitutionalStatus.NONE
    definition_period = MONTH
    label = "Illinois AABD Institutional Status"
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.70"
