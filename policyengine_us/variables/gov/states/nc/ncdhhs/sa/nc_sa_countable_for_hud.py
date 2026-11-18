from policyengine_us.model_api import *


class nc_sa_countable_for_hud(Variable):
    value_type = float
    entity = Person
    label = "North Carolina Special Assistance countable for HUD"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NC
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf#page=47",
        # 24 CFR 5.609(b)(12)(ii)
        "https://www.law.cornell.edu/cfr/text/24/5.609",
    )

    def formula(person, period, parameters):
        category = person("nc_sa_care_setting", period)
        c = category.possible_values
        excluded = (category == c.IN_HOME) | (category == c.IN_HOME_ENHANCED)
        return person("nc_sa", period) * ~excluded
