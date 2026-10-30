from policyengine_us.model_api import *


class social_security_birth_day(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = "Social Security birth day"
    documentation = "Optional supplied day of birth for the entitlement_dates population claiming scenario. Zero means unavailable; with a known birth month, day 2 is the explicit approximation and raises the proxy flag. No formula or uprating. Exact dates preserve SSA age attainment on the day before a birthday, including January 1 births."
