from policyengine_us.model_api import *


class sd_ssp_care_days(Variable):
    value_type = int
    entity = Person
    label = "Covered South Dakota SSP care days"
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:46:04:15"

    def formula(person, period, parameters):
        return period.days
