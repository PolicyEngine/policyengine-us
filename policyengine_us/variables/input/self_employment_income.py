from policyengine_us.model_api import *


class self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "self-employment income"
    unit = USD
    documentation = "Self-employment non-farm income."
    definition_period = YEAR
    adds = [
        "self_employment_income_before_lsr",
        "self_employment_income_behavioral_response",
    ]
    reference = "https://www.law.cornell.edu/uscode/text/26/1402#a"
    uprating = "calibration.gov.irs.soi.self_employment_income"
