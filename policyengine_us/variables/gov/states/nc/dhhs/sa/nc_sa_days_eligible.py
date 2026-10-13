from policyengine_us.model_api import *


class nc_sa_days_eligible(Variable):
    value_type = int
    entity = Person
    label = "North Carolina SA eligible days in initial month"
    definition_period = MONTH
    defined_for = StateCode.NC
    documentation = "For an initial partial month, days from the date all eligibility conditions are satisfied through month end, including the first eligible day. Ongoing months default to the full month. This does not implement a discharge-month settlement."
    reference = (
        # PDF pages 209-210
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf#page=209",
        # PDF pages 42-43
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf#page=42",
    )

    def formula(person, period, parameters):
        return period.days
