from policyengine_us.model_api import *


class ssi_food_from_others_only_on_or_after_food_exclusion(Variable):
    value_type = bool
    entity = Person
    label = (
        "All food from others this month came on or after the SSI food exclusion date"
    )
    documentation = (
        "Whether all of the food this person received from others in the "
        "month was received or paid for on or after the date food stopped "
        "counting as in-kind support and maintenance (September 30, 2024). "
        "Only matters in the month that date falls in."
    )
    definition_period = MONTH
    default_value = False
    reference = (
        "https://www.govinfo.gov/content/pkg/FR-2024-03-27/pdf/2024-06464.pdf#page=1",
        "https://secure.ssa.gov/apps10/referencearchive.nsf/links/09202024102751AM",
    )
