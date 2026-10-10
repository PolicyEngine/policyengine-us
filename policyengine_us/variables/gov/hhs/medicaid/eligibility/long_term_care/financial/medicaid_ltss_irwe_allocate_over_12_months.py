from policyengine_us.model_api import *


class medicaid_ltss_irwe_allocate_over_12_months(Variable):
    value_type = bool
    entity = Person
    label = "Elected 12-month allocation of a Medicaid LTSS impairment-related payment"
    definition_period = MONTH
    default_value = False
    documentation = (
        "Whether this person elects to allocate the nonrecurring impairment-related "
        "payment reported in this month over twelve consecutive months beginning "
        "with this month. Report the election only in the original payment month. "
        "A false election deducts the payment only in that month. This records "
        "the person's choice, not a deductible amount or eligibility result. "
        "Separate payments made in later months retain their own election."
    )
    reference = "https://www.ssa.gov/OP_Home/cfr20/416/416-0976.htm"

    def formula(person, period, parameters):
        # Transaction facts apply only to the explicitly reported month.
        # A zero fallback prevents Core from carrying or uprating past inputs.
        return person.empty_array()
