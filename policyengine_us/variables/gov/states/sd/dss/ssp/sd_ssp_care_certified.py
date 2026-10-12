from policyengine_us.model_api import *


class sd_ssp_care_certified(Variable):
    value_type = bool
    entity = Person
    label = "Certified for South Dakota nonwaiver optional supplemental care"
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:46:04:15"
    documentation = "Approved placement, care needs, benefit pursuit and nonfinancial program requirements; excludes Medicaid waiver services."
