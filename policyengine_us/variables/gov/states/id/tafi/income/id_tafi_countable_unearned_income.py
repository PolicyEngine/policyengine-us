from policyengine_us.model_api import *


class id_tafi_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho TAFI countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.250"
    )
    defined_for = StateCode.ID

    # Per IDAPA 16.03.08.250: 100% of unearned income is counted
    adds = ["tanf_gross_unearned_income"]
