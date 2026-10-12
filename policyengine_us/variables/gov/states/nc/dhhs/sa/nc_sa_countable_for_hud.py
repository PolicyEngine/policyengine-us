from policyengine_us.model_api import *


class nc_sa_countable_for_hud(Variable):
    value_type = float
    entity = Person
    label = "North Carolina State Assistance countable for HUD"
    definition_period = MONTH
    unit = USD
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf"

    def formula(person, period, parameters):
        category = person("nc_sa_care_setting", period)
        c = category.possible_values
        excluded = (category == c.IN_HOME) | (category == c.IN_HOME_ENHANCED)
        return person("nc_sa", period) * ~excluded
