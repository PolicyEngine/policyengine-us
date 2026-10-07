from policyengine_us.model_api import *


class medicaid_ltss_irwe_nonrecurring_reimbursement(Variable):
    value_type = float
    entity = Person
    label = "Reimbursement for a nonrecurring Medicaid LTSS impairment-related payment"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Amount of this person's nonrecurring impairment-related payment paid "
        "by another source or reimbursed, available for reimbursement, or expected "
        "to be reimbursed. Report this amount in the original payment month, even "
        "if reimbursement arrives later. The model nets this factual amount against "
        "the purchase or service payment before applying any allocation election."
    )
    reference = "https://www.ssa.gov/OP_Home/cfr20/416/416-0976.htm"

    def formula(person, period, parameters):
        # Transaction facts apply only to the explicitly reported month.
        # A zero fallback prevents Core from carrying or uprating past inputs.
        return person.empty_array()
