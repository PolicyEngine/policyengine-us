from policyengine_us.model_api import *


class pr_earned_income_credit_eligible_people(Variable):
    value_type = int
    entity = TaxUnit
    label = "Puerto Rico earned income credit eligible people"
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/schedule_ct_rev._jul_5_23_informative_-_instructions.pdf#page=1"

    adds = ["pr_earned_income_credit_eligible_person"]
