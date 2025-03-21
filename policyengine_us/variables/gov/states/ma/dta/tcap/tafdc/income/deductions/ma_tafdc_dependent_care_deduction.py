from policyengine_us.model_api import *


class ma_tafdc_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) dependent care deduction"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275"  # (A)
    defined_for = StateCode.MA

    adds = ["ma_tafdc_dependent_care_deduction_person"]
