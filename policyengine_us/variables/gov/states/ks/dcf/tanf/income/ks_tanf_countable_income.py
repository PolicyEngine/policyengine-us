from policyengine_us.model_api import *


class ks_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-110",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm7110.htm",
    )
    defined_for = StateCode.KS
    adds = [
        "ks_tanf_countable_earned_income",
        "tanf_gross_unearned_income",
    ]
