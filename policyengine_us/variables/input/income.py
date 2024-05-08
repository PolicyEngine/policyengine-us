from policyengine_us.model_api import *


label = "Income"


class employment_income_before_lsr(Variable):
    value_type = float
    entity = Person
    label = "employment income before labor supply responses"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.employment_income"


class self_employment_income_before_lsr(Variable):
    value_type = float
    entity = Person
    label = "self-employment income before labor supply responses"
    unit = USD
    definition_period = YEAR
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


class self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "self-employment income"
    unit = USD
    documentation = "Self-employment non-farm income."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.self_employment_income"
    adds = [
        "self_employment_income_before_lsr",
        "self_employment_income_behavioral_response",
    ]


class emp_self_emp_ratio(Variable):
    value_type = float
    entity = Person
    label = "employment-to-self-employment income ratio"
    unit = "/1"
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)
        total_earnings = employment_income + self_employment_income
        return where(total_earnings > 0, employment_income / total_earnings, 1)


class farm_income(Variable):
    value_type = float
    entity = Person
    label = "farm income"
    unit = USD
    documentation = "Income from agricultural businesses. Do not include this income in self-employment income."
    definition_period = YEAR
