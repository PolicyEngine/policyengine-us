from policyengine_us.model_api import *


class medicaid_ltss_irwe_monthly_business_expenses(Variable):
    value_type = float
    entity = Person
    label = "Monthly Medicaid LTSS impairment-related payments already deducted as business expenses"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Actual amount of this person's reported monthly impairment-related "
        "payments already deducted in calculating net self-employment income. "
        "Report the overlapping cost before applying Medicaid LTSS income rules. "
        "The model removes this amount from the expense deduction to avoid "
        "deducting the same business cost twice. Exclude amounts also reported "
        "as nonrecurring business expenses."
    )
    reference = "https://www.ssa.gov/OP_Home/cfr20/416/416-0976.htm"

    def formula(person, period, parameters):
        # Transaction facts apply only to the explicitly reported month.
        # A zero fallback prevents Core from carrying or uprating past inputs.
        return person.empty_array()
