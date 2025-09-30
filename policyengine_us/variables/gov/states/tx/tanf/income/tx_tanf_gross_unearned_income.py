from policyengine_us.model_api import *


class tx_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Texas TANF gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits",
        "https://www.law.cornell.edu/regulations/texas/1-TAC-372-601",
    )
    defined_for = StateCode.TX

    adds = "gov.states.tx.tanf.income.sources.unearned"
