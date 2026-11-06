from policyengine_us.model_api import *


class hi_temporary_disability_insurance_qualified(Variable):
    value_type = bool
    entity = Person
    label = "Wages count toward the Hawaii temporary disability insurance contribution"
    documentation = (
        "HRS 392-43(b)(1) counts wages from a payroll period only if the prior "
        "52 weeks hold enough wages and enough weeks with enough paid hours. "
        "The model holds no prior-year work history, so this annual proxy tests "
        "the simulation year's wages, weeks worked and usual weekly hours. Zero "
        "weeks or zero hours mean the value went unreported, so that part of "
        "the test passes."
    )
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://data.capitol.hawaii.gov/hrscurrent/Vol07_Ch0346-0398/HRS0392/HRS_0392-0043.htm",
        "https://data.capitol.hawaii.gov/hrscurrent/Vol07_Ch0346-0398/HRS0392/HRS_0392-0043_0005.htm",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.hi.tax.payroll.temporary_disability_insurance.qualification
        wages = person("payroll_tax_gross_wages", period)
        weeks = person("weeks_worked", period)
        hours = person("weekly_hours_worked_before_lsr", period)
        meets_wages = wages >= p.minimum_wages
        meets_weeks = (weeks == 0) | (weeks >= p.minimum_weeks)
        meets_hours = (hours == 0) | (hours >= p.minimum_weekly_hours)
        return meets_wages & meets_weeks & meets_hours
