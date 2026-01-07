from policyengine_us.model_api import *


class nj_wfnj_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey WFNJ gross earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-9"
    )
    adds = "gov.states.nj.njdhs.wfnj.income.earned"
