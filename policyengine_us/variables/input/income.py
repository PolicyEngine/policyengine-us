from policyengine_us.model_api import *


label = "Income"


class employment_income_before_lsr(Variable):
    value_type = float
    entity = Person
    label = "employment income before labor supply responses"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/3401#a"
    uprating = "calibration.gov.irs.soi.employment_income"


class self_employment_income_before_lsr(Variable):
    value_type = float
    entity = Person
    label = "self-employment income before labor supply responses"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1402#a"
    uprating = "calibration.gov.irs.soi.self_employment_income"


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
