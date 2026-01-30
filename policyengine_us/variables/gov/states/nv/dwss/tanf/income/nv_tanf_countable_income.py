from policyengine_us.model_api import *


class nv_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nevada TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-2/"
    defined_for = StateCode.NV

    adds = [
        "nv_tanf_countable_earned_income",
        "tanf_gross_unearned_income",
    ]
