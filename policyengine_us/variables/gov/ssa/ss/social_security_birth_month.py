from policyengine_us.model_api import *


class social_security_birth_month(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = "Social Security birth month"
    documentation = "Supplied birth month, 1 through 12, for the entitlement_dates population claiming scenario. Zero means unavailable. No formula or uprating. Used with the birth year; a missing birth day uses the explicit day-2 convention and raises the proxy flag. An exact ss_calculator_birth_date can supply the complete date instead."
