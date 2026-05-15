from policyengine_us.model_api import *


class ArSraCareType(Enum):
    REGULAR = "Regular"
    NIGHT_WEEKEND = "Night/Weekend"
    SN1 = "Special Needs Level 1"
    SN2 = "Special Needs Level 2"
    SN3 = "Special Needs Level 3"


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
    )
