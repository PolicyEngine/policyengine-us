from policyengine_us.model_api import *


class pr_additional_child_tax_credit_eligibility(Variable):
    value_type = int
    entity = TaxUnit
    label = "Eligiblity for children to qualify for the Puerto Rico additional child tax credit"
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        num_children = tax_unit("pr_child_tax_credit_number_eligible_children", period)
        other_dependents = tax_unit("tax_unit_dependents", period)
        income_threshold = num_children * 2000 + other_dependents * 500 # threshold

        # eligibility: at least one child under age of 17
        # must not have too high of an income
        income_eligible = tax_unit("pr_actc_modified_income_calculation") < income_threshold
        
        return (num_children >= 1) & income_eligible