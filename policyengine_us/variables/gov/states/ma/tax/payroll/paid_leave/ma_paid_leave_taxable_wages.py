from policyengine_us.model_api import *


class ma_paid_leave_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts PFML taxable wages"
    documentation = (
        "Wages subject to Massachusetts PFML contributions, including federal "
        "pre-tax payroll deductions and capped at the Social Security "
        "contribution and benefit base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        return min_(
            max_(0, person("employment_income", period)),
            parameters(period).gov.irs.payroll.social_security.cap,
        )


class employer_total_ma_paid_leave_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Employer total Massachusetts PFML taxable wages"
    documentation = (
        "Aggregate employer wages subject to Massachusetts PFML contributions "
        "for employer-only payroll tax calculations."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        return person("employer_total_taxable_earnings_for_social_security", period)
