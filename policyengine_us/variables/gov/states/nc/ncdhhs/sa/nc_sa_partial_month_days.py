from policyengine_us.model_api import *


class nc_sa_partial_month_days(Variable):
    value_type = int
    entity = Person
    label = "North Carolina SA eligible days in a partial first month"
    definition_period = MONTH
    defined_for = StateCode.NC
    default_value = 0
    documentation = "For a first month in which eligibility begins after the first day, the days from the first eligible day through the end of the month. Leave at 0 for a full month of eligibility. This does not implement a discharge-month settlement."
    reference = (
        # PDF pages 209-210
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf#page=209",
        # PDF pages 42-43
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf#page=42",
    )
