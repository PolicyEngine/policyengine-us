from policyengine_us.model_api import *


class pr_additional_child_tax_credit_eligibility(Variable):
    value_type = int
    entity = TaxUnit
    label = "Eligiblity for children to qualify for the Puerto Rico additional child tax credit"
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        num_children = tax_unit("pr_child_tax_credit_number_eligible_children", period)

        # eligibility: at least one child under age of 17
        return (num_children >= 1)