from policyengine_us.model_api import *


class pr_child_tax_credit_number_eligible_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Eligiblity for children to qualify for the Puerto Rico child tax credit"
    definition_period = YEAR
    reference = ""

    adds = ["pr_child_tax_credit_child_eligibility"]