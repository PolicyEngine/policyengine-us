from policyengine_us.model_api import *


class sd_ssp_care_income_not_applied(Variable):
    value_type = bool
    entity = Person
    label = "South Dakota care month has no income contribution"
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:46:06:09"
    documentation = "Defaults to true for a partial care month under ARSD 67:46:06:09. Set to false for a month in which the recipient died or transferred to another long-term care facility."

    def formula(person, period, parameters):
        return person("sd_ssp_care_days", period) < period.days
