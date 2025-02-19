from policyengine_us.model_api import *


class pr_earned_income_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Puerto Rico earned income credit eligible unit"
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/schedule_ct_rev._jul_5_23_informative_-_instructions.pdf#page=1"
    defined_for = "pr_earned_income_credit_eligible_people"

    def formula(tax_unit, period, parameters):
        # list of eligible people in the tax unit from the adds function
        num_eligible_people = tax_unit(
            "pr_earned_income_credit_eligible_people", period
        )
        eligible_people_exist = num_eligible_people > 0
        return eligible_people_exist
