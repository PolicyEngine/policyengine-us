from policyengine_us.model_api import *


class medicaid_ltss_irwe_working_when_paid(Variable):
    value_type = bool
    entity = Person
    label = "Worked when Medicaid LTSS impairment-related payments were made"
    definition_period = MONTH
    default_value = False
    documentation = (
        "Whether this person was working in the month the reported impairment-related "
        "payments were made and needed and used the items or services for that work. "
        "Report this fact in each payment month, including the original month of a "
        "nonrecurring purchase or service payment. The ordinary payment-month rules "
        "also require earned income to be received then; the model derives receipt "
        "from gross earned income. Payments before work begins, before earned income "
        "is first received, or after work stops need separate timing facts and are "
        "outside this screen's current expense calculation."
    )
    reference = "https://www.ssa.gov/OP_Home/cfr20/416/416-0976.htm"

    def formula(person, period, parameters):
        # Transaction facts apply only to the explicitly reported month.
        # A zero fallback prevents Core from carrying or uprating past inputs.
        return person.empty_array()
