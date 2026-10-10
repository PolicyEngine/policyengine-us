from policyengine_us.model_api import *


class medicaid_ltss_irwe_nonrecurring_payment(Variable):
    value_type = float
    entity = Person
    label = (
        "Nonrecurring payment for Medicaid LTSS impairment-related items or services"
    )
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "One-time money payments this person made for impairment-related items or services "
        "needed and used to work, reported in the month of payment. For a durable "
        "item, report the full purchase payment in its actual payment month; unpaid "
        "purchase balances are not payments. Multiple payments made in the same "
        "month with the same allocation election can be combined. Report the "
        "actual amount before reimbursements or business-expense deductions, "
        "excluding amounts also reported as monthly payments. Report cash, check, "
        "card, or other money payments, not payments in kind. This fact and the "
        "payment month's allocation election drive the model's monthly deduction. "
        "An ordinary one-time downpayment may be reported separately from monthly "
        "installments under 416.976(e)(2). The special combined downpayment-plus-"
        "installment allocation election under (e)(3) is outside this input."
    )
    reference = "https://www.ssa.gov/OP_Home/cfr20/416/416-0976.htm"

    def formula(person, period, parameters):
        # Transaction facts apply only to the explicitly reported month.
        # A zero fallback prevents Core from carrying or uprating past inputs.
        return person.empty_array()
