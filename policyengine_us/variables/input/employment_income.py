from policyengine_us.model_api import *


class employment_income(Variable):
    value_type = float
    entity = Person
    label = "employment income"
    documentation = "Wages and salaries, including tips and commissions."
    unit = USD
    definition_period = YEAR
    adds = [
        "employment_income_before_lsr",
        "employment_income_behavioral_response",
    ]
    reference = "https://www.law.cornell.edu/uscode/text/26/3401#a"
    uprating = "calibration.gov.irs.soi.employment_income"
