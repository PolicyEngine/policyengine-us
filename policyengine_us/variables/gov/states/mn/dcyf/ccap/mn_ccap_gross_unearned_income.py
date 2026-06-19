from policyengine_us.model_api import *


class mn_ccap_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Minnesota CCAP gross unearned income"
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.06",
        "https://www.revisor.mn.gov/rules/3400.0170/",
    )
    adds = "gov.states.mn.dcyf.ccap.income.countable_income.unearned"
