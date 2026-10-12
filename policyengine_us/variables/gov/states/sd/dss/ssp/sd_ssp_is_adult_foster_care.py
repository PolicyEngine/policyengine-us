from policyengine_us.model_api import *


class sd_ssp_is_adult_foster_care(Variable):
    value_type = bool
    entity = Person
    label = "South Dakota SSP care is licensed adult foster care"
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:46:04:15"
