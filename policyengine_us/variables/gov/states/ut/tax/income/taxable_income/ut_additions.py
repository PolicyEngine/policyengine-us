from policyengine_us.model_api import *


class ut_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah additions to income"
    unit = USD
    documentation = "Form TC-40, line 5"
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323"
