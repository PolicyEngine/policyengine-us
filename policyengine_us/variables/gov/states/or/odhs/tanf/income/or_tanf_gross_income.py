from policyengine_us.model_api import *


class or_tanf_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oregon TANF gross income"
    unit = USD
    definition_period = MONTH
    reference = "https://oregon.public.law/rules/oar_461-140-0010"
    defined_for = StateCode.OR

    adds = [
        "tanf_gross_earned_income",
        "tanf_gross_unearned_income",
    ]
