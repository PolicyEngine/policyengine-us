from policyengine_us.model_api import *


class self_employment_income_before_lsr(Variable):
    value_type = float
    entity = Person
    label = "self-employment income before labor supply responses"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1402#a"
    uprating = "calibration.gov.irs.soi.self_employment_income"
