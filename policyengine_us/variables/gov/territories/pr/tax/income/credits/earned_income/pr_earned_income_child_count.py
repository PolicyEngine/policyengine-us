from policyengine_us.model_api import *


class pr_earned_income_child_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Puerto Rico EITC-qualifying children"
    definition_period = YEAR
    reference = 

    adds = ["is_child_dependent"]
