from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction_eligible_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Eligible children for the Montana child dependent care expense deduction "
    definition_period = YEAR
    reference = "https://casetext.com/statute/montana-code/title-15-taxation/chapter-30-individual-income-tax/part-21-rate-and-general-provisions/section-15-30-2131-repealed-effective-112024-temporary-deductions-allowed-in-computing-net-income"
    defined_for = StateCode.MT

    adds = ["mt_child_dependent_care_expense_deduction_eligible_child"]
