from policyengine_us.model_api import *


class nc_sa_facility_rate(Variable):
    value_type = float
    entity = Person
    label = "North Carolina SA lower contracted monthly facility rate"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NC
    default_value = 0
    documentation = "The monthly rate a facility charges a Special Assistance resident when it contracts for less than the published rate. Leave at 0 to use the published rate. In-home payments always use the published rate."
    reference = (
        # PDF pages 204-206
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf#page=204",
    )
