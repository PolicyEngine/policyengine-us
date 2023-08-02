from policyengine_us.model_api import *


class nj_tanf_countable_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey TANF countable gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    adds = "gov.states.nj.njdhs.tanf.income.unearned"
