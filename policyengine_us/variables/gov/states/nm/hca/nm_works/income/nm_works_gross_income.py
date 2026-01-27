from policyengine_us.model_api import *


class nm_works_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico Works gross income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0520.html"
    defined_for = StateCode.NM

    adds = ["tanf_gross_earned_income", "tanf_gross_unearned_income"]
