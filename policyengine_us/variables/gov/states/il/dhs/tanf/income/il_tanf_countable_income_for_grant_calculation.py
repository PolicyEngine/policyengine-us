from policyengine_us.model_api import *


class il_tanf_countable_income_for_grant_calculation(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) countable income for grant calculation"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.155"
    defined_for = StateCode.IL

    adds = [
        "il_tanf_countable_earned_income_for_grant_calculation",
        "il_tanf_countable_unearned_income",
    ]
