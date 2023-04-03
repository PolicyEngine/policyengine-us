from policyengine_us.model_api import *


class ny_tanf_countable_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF countable gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    adds = "gov.states.ny.otda.tanf.income.unearned"
