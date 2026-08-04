from policyengine_us.model_api import *


class co_famli_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Colorado FAMLI taxable wages"
    documentation = (
        "Wages subject to Colorado FAMLI premiums, including federal pre-tax "
        "payroll deductions and capped at the Social Security contribution "
        "and benefit base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        return min_(
            max_(0, person("employment_income", period)),
            parameters(period).gov.irs.payroll.social_security.cap,
        )


class employer_total_co_famli_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Employer total Colorado FAMLI taxable wages"
    documentation = (
        "Aggregate employer wages subject to Colorado FAMLI premiums for "
        "employer-only payroll tax calculations."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        return person("employer_total_taxable_earnings_for_social_security", period)
