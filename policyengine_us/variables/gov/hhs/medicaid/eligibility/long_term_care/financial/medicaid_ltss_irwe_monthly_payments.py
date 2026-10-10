from policyengine_us.model_api import *


class medicaid_ltss_irwe_monthly_payments(Variable):
    value_type = float
    entity = Person
    label = "Monthly payments for Medicaid LTSS impairment-related items and services"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Money this person paid in the modeled month for recurring items or services "
        "needed and used to work because of an impairment. Report the actual payments "
        "before reimbursement or business-expense deductions. Include monthly "
        "installments and rentals, and exclude any amount also reported as a "
        "nonrecurring payment. Report cash, check, card, or other money payments, "
        "not payments in kind. The model derives the deductible amount, including "
        "reimbursement netting and claimant eligibility; this input is not an "
        "allocated or policy-qualified deduction."
    )
    reference = "https://www.ssa.gov/OP_Home/cfr20/416/416-0976.htm"

    def formula(person, period, parameters):
        # Transaction facts apply only to the explicitly reported month.
        # A zero fallback prevents Core from carrying or uprating past inputs.
        return person.empty_array()
