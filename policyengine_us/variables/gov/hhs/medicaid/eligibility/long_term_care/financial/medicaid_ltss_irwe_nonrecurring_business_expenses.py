from policyengine_us.model_api import *


class medicaid_ltss_irwe_nonrecurring_business_expenses(Variable):
    value_type = float
    entity = Person
    label = "Nonrecurring Medicaid LTSS impairment-related payment already deducted as a business expense"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Actual amount of this person's nonrecurring impairment-related payment "
        "already deducted in calculating net self-employment income. Report it "
        "in the original payment month before applying Medicaid LTSS income rules. "
        "The model removes the overlapping amount before allocation to avoid "
        "deducting the same business cost twice."
    )
    reference = "https://www.ssa.gov/OP_Home/cfr20/416/416-0976.htm"

    def formula(person, period, parameters):
        # Transaction facts apply only to the explicitly reported month.
        # A zero fallback prevents Core from carrying or uprating past inputs.
        return person.empty_array()
