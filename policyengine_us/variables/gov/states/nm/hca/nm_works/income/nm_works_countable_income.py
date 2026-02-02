from policyengine_us.model_api import *


class nm_works_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico Works countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0520.html"
    defined_for = StateCode.NM
    adds = [
        "nm_works_countable_earned_income",
        "nm_works_countable_unearned_income",
    ]
