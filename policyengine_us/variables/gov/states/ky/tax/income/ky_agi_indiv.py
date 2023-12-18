from policyengine_us.model_api import *


class ky_agi_indiv(Variable):
    value_type = float
    entity = Person
    label = (
        "Kentucky adjusted gross income when married couples file separately"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11"
    defined_for = StateCode.KY
    adds = ["ky_additions", "adjusted_gross_income"]
    subtracts = ["ky_subtractions"]
