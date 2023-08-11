from policyengine_us.model_api import *


class hi_lihrtc_disabled(Variable):
    value_type = bool
    entity = Person
    label = "Disabled for no extra exemptions"
    definition_period = YEAR
    reference = " https://files.hawaii.gov/tax/legal/har/har_235.pdf#page=105"  # §18-235-55.7 (b)

    def formula(person, period, parameters):
        
        return person("is_disabled", period)