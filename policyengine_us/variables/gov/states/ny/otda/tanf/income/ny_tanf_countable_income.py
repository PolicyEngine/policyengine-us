from policyengine_us.model_api import *


class ny_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/policy/directives/2022/ADM/22-ADM-11.pdf#page=3",
    )

    adds = [
        "ny_tanf_countable_earned_income",
        "tanf_gross_unearned_income",
    ]
