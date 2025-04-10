from policyengine_us.model_api import *


class IllinoisAABDInstitutionalStatus(Enum):
    A = "A"  # Institutional Status A
    B = "B"  # Institutional Status B
    C = "C"  # Institutional Status C
    D = "D"  # Institutional Status D
    E = "E"  # Institutional Status E
    F = "F"  # Institutional Status F
    G = "G"  # Institutional Status G
    H = "H"  # Institutional Status H
    I = "I"  # Institutional Status I
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
