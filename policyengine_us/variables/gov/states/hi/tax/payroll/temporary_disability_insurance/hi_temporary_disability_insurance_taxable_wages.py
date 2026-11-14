from policyengine_us.model_api import *


class hi_temporary_disability_insurance_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Hawaii temporary disability insurance taxable wages"
    documentation = (
        "Wages subject to the Hawaii temporary disability insurance employee "
        "contribution. HRS 392-43(b)(2) caps wages week by week, so the annual "
        "cap multiplies the maximum weekly wage base by weeks worked, or by 52 "
        "when weeks worked went unreported. An even weekly wage reaches the "
        "largest amount the weekly cap allows, so this amount is an upper limit "
        "for a worker with one employer who passes the annual qualification "
        "test."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.HI
    reference = (
        "https://data.capitol.hawaii.gov/hrscurrent/Vol07_Ch0346-0398/HRS0392/HRS_0392-0043.htm",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.tax.payroll.temporary_disability_insurance
        wages = person("hi_temporary_disability_insurance_wages", period)
        weeks = person("weeks_worked", period)
        counted_weeks = where(weeks > 0, min_(weeks, WEEKS_IN_YEAR), WEEKS_IN_YEAR)
        capped_wages = min_(wages, p.maximum_weekly_wage_base * counted_weeks)
        qualified = person("hi_temporary_disability_insurance_qualified", period)
        return where(qualified, capped_wages, 0)
