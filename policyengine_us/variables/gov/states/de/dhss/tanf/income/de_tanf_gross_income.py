from policyengine_us.model_api import *


class de_tanf_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF gross income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008"
    defined_for = StateCode.DE

    adds = ["tanf_gross_earned_income", "tanf_gross_unearned_income"]
