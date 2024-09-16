from policyengine_us.model_api import *


class ut_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah subtractions"
    unit = USD
    documentation = "Form TC-40, line 8"
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323"
