from policyengine_us.model_api import *


class ri_works_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island Works countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/rhode-island/218-RICR-20-00-2.15",
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
    )
    defined_for = StateCode.RI

    adds = [
        "ri_works_countable_earned_income",
        "ri_works_countable_unearned_income",
    ]
