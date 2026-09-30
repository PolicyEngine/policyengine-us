from policyengine_us.model_api import *


class snap_work_requirement_weekly_earnings(Variable):
    value_type = float
    entity = Person
    label = "Weekly earnings for the SNAP 30-hour work registration exemption"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Weekly earnings from employment and non-farm self-employment, "
        "compared with the federal minimum wage times 30 hours in the "
        "earnings-equivalent prong of the 30-hour work registration "
        "exemption (7 U.S.C. 2015(d)(2)(E); 7 CFR 273.7(b)(1)(vii)). Annual "
        "earnings are averaged over all 52 weeks, the same denominator "
        "snap_work_requirement_weekly_hours uses: earnings per week worked "
        "would restore the exemption for every part-year worker whose usual "
        "hours are 30 or more at a wage of at least the minimum. With "
        "gov.simulation.snap_work_hours_use_weeks_worked set to false, "
        "earnings are divided by weeks worked instead (52 when weeks worked "
        "are not reported). Before-labor-supply-response inputs avoid a "
        "SNAP to labor supply to SNAP cycle, and self-employment losses are "
        "floored at zero as in snap_gross_self_employment_income_person. "
        "Known limitation: under annual averaging, a part-year worker whose "
        "annual earnings reach the federal minimum wage x 30 hours x 52 "
        "weeks ($11,310 at $7.25 an hour) is exempt in every month of the "
        "year."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#d_2",
        "https://www.law.cornell.edu/cfr/text/7/273.7#b_1_vii",
    )

    def formula(person, period, parameters):
        earnings = (
            max_(person("employment_income_before_lsr", period), 0)
            + max_(person("self_employment_income_before_lsr", period), 0)
            + max_(person("sstb_self_employment_income_before_lsr", period), 0)
        )
        if parameters(period).gov.simulation.snap_work_hours_use_weeks_worked:
            return earnings / WEEKS_IN_YEAR
        weeks = person("weeks_worked", period)
        weeks_divisor = where(weeks > 0, min_(weeks, WEEKS_IN_YEAR), WEEKS_IN_YEAR)
        return earnings / weeks_divisor
