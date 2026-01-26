from policyengine_us.model_api import *


class ny_tanf_countable_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF countable gross unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/policy/directives/1997/ADM/97_ADM-23.pdf#page=3"
    )

    adds = "gov.hhs.tanf.cash.income.sources.unearned"
