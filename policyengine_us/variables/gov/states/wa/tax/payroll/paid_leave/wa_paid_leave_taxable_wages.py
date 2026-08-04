from policyengine_us.model_api import *


class wa_paid_leave_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Washington paid leave taxable wages"
    documentation = (
        "Wages subject to Washington Paid Family and Medical Leave premiums, "
        "excluding tips and capped at the Social Security contribution and "
        "benefit base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA

    def formula(person, period, parameters):
        return min_(
            person("wa_long_term_care_taxable_wages", period),
            parameters(period).gov.irs.payroll.social_security.cap,
        )


class employer_total_wa_paid_leave_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Employer total Washington paid leave taxable wages"
    documentation = (
        "Aggregate employer wages subject to Washington Paid Family and "
        "Medical Leave premiums for employer-only payroll tax calculations."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA

    def formula(person, period, parameters):
        return person("employer_total_taxable_earnings_for_social_security", period)
