from policyengine_us.model_api import *


class self_employment_income_last_year(Variable):
    value_type = float
    entity = Person
    label = "self-employment income last year"
    documentation = "Self-employment income in prior year."
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.self_employment_income"


class previous_year_income_available(Variable):
    value_type = bool
    entity = Person
    label = "Prior-year income available"
    documentation = "Whether prior-year income was available in the survey."
    definition_period = YEAR
