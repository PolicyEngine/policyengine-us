from policyengine_us.model_api import *


class social_security_retirement_claim_age_months(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = "Retirement age in whole months at first entitlement"
    documentation = "Pure supplied retirement claim age in whole months: 62 years 3 months is 747. Zero means unavailable. No formula or uprating; projected dataset columns must supply the value separately for each scoring year. The selected supplied_claim_age scenario accepts ages 62 through 70."
