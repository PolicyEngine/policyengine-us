from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction_eligible_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Eligible children for the Montana child dependent care expense deduction "
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/2441-M_2022.pdf#page=1"
    defined_for = StateCode.MT

    adds = ["mt_child_dependent_care_expense_deduction_eligible_child"]