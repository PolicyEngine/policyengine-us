from policyengine_us.model_api import *


class medicaid_ltss_irwe_monthly_reimbursements(Variable):
    value_type = float
    entity = Person
    label = "Reimbursements for monthly Medicaid LTSS impairment-related payments"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Amount of this person's reported monthly impairment-related payments "
        "paid by another source or reimbursed, available for reimbursement, or "
        "expected to be reimbursed. Report the reimbursement against the payment "
        "month, even if the reimbursement arrives later. Include private insurance, "
        "Medicare, Medicaid, and other sources. The model nets this factual amount "
        "against monthly payments rather than asking for an out-of-pocket deduction."
    )
    reference = "https://www.ssa.gov/OP_Home/cfr20/416/416-0976.htm"

    def formula(person, period, parameters):
        # Transaction facts apply only to the explicitly reported month.
        # A zero fallback prevents Core from carrying or uprating past inputs.
        return person.empty_array()
