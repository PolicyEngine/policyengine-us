from policyengine_us.model_api import *


class pr_earned_income_child_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Puerto Rico EITC-qualifying children"
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/schedule_ct_rev._jul_5_23_informative_-_instructions.pdf#page=3"

    adds = ["is_child_dependent"]
