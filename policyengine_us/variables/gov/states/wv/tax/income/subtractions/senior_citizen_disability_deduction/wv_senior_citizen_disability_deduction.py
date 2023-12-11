from policyengine_us.model_api import *


class wv_senior_citizen_disability_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia senior citizen or disability deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV

    adds = ["wv_senior_citizen_disability_deduction_person"]
