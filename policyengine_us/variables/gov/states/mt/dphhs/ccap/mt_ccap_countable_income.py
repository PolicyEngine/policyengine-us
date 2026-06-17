from policyengine_us.model_api import *


class mt_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Best Beginnings Child Care Scholarship countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.MT
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.102",
        "https://dphhs.mt.gov/assets/ecfsd/childcare/policymanual/CC26IncomeTable070718.pdf#page=2",
    )

    adds = "gov.states.mt.dphhs.ccap.income.countable_income.sources"
