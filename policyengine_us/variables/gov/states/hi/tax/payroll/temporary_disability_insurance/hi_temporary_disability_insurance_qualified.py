from policyengine_us.model_api import *


class hi_temporary_disability_insurance_qualified(Variable):
    value_type = bool
    entity = Person
    label = "Wages count toward the Hawaii temporary disability insurance contribution"
    documentation = (
        "HRS 392-43(b)(1) counts wages from a payroll period only if the prior "
        "52 weeks hold enough wages and enough weeks with enough paid hours. "
        "This annual proxy passes a worker in either of two ways. The first "
        "tests the simulation year's wages, weeks worked and usual weekly "
        "hours, and there zero weeks or zero hours mean the value went "
        "unreported, so that part of the test passes. The second tests the "
        "previous year's weeks worked and usual weekly hours, and it needs "
        "both on file. A single year of inputs leaves the previous year at "
        "zero, so a worker with a short year and no history on file does not "
        "pass. Usual weekly hours stand in for each week's hours, so a worker "
        "whose usual hours fall under the minimum does not pass even with "
        "enough qualifying weeks."
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
        wages = person("hi_temporary_disability_insurance_wages", period)
        weeks = person("weeks_worked", period)
        hours = person("weekly_hours_worked_before_lsr", period)
        meets_wages = wages >= p.minimum_wages
        meets_weeks = (weeks == 0) | (weeks >= p.minimum_weeks)
        meets_hours = (hours == 0) | (hours >= p.minimum_weekly_hours)
        passes_in_year = meets_wages & meets_weeks & meets_hours
        # The previous year passes only on positive evidence, because zero
        # there means no history on file. The minimum weeks and hours make
        # 280 paid hours, which reach the minimum wages at about $1.43 an
        # hour, so the wages part of the test needs no separate read.
        last_year = period.last_year
        weeks_last_year = person("weeks_worked", last_year)
        hours_last_year = person("weekly_hours_worked_before_lsr", last_year)
        passes_last_year = (weeks_last_year >= p.minimum_weeks) & (
            hours_last_year >= p.minimum_weekly_hours
        )
        return passes_in_year | passes_last_year
