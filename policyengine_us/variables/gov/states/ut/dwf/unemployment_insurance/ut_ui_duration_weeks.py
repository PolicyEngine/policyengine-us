from policyengine_us.model_api import *


class ut_ui_duration_weeks(Variable):
    value_type = int
    entity = Person
    label = "Utah UI potential duration in weeks"
    unit = "week"
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title35A/Chapter4/35A-4-S401.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dwf.unemployment_insurance
        base_period_wages = person("ut_ui_base_period_wages", period)
        weekly_benefit_amount = person("ut_ui_weekly_benefit_amount", period)

        # § 35A-4-401(4)(b): potential duration =
        #   floor(floor(0.27 × total base-period wages) / WBA),
        # clamped to [min_weeks, max_weeks] (10-26 weeks).
        # Guard against divide-by-zero when WBA = 0 (not monetarily eligible
        # or WBA capped to zero).
        has_wba = weekly_benefit_amount > 0
        numerator = np.floor(p.benefit.duration.multiplier * base_period_wages)
        # Use a safe divisor of 1 where WBA is zero; the where() below
        # overrides the result with 0 in that case.
        safe_wba = where(has_wba, weekly_benefit_amount, 1)
        raw_weeks = np.floor(numerator / safe_wba)
        clamped_weeks = np.clip(
            raw_weeks, p.benefit.duration.min_weeks, p.benefit.duration.max_weeks
        )
        return where(has_wba, clamped_weeks, 0)
