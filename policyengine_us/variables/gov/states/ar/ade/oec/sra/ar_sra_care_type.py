from policyengine_us.model_api import *


class ArSraCareType(Enum):
    REGULAR = "Regular"
    NIGHT_WEEKEND = "Night/Weekend"
    SN1 = "Special Needs Level 1"
    SN2 = "Special Needs Level 2"
    SN3 = "Special Needs Level 3"


# Per FSU Procedural Manual §5.6.1: SN1 = no extra staff, SN2 = temporary extra
# staff, SN3 = full-time 1:1 staff, set by a licensed medical practitioner. We
# don't track that operational determination at the moment, so this is a bare
# input — users modeling a known case set it directly.
class ar_sra_care_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = ArSraCareType
    default_value = ArSraCareType.REGULAR
    definition_period = MONTH
    defined_for = StateCode.AR
    label = "Arkansas SRA care type"
    reference = (
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=32",
    )
