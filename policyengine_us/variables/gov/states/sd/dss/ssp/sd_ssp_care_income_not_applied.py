from policyengine_us.model_api import *


class sd_ssp_care_income_not_applied(Variable):
    value_type = bool
    entity = Person
    label = "South Dakota care month has no income contribution"
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:46:06:09"
    documentation = "Certified partial-month exception under ARSD 67:46:06:09; excludes death and transfer months and cases with an assessed contribution."
