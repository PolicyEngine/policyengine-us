from policyengine_us.model_api import *


class employment_income_before_lsr(Variable):
    value_type = float
    entity = Person
    label = "employment income before labor supply responses"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/3401#a"
    uprating = "calibration.gov.irs.soi.employment_income"
