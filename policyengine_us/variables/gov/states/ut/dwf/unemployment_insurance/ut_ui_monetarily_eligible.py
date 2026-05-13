from policyengine_us.model_api import *


class ut_ui_monetarily_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Monetarily eligible for Utah Unemployment Insurance"
    definition_period = YEAR
    reference = (
        "https://le.utah.gov/xcode/Title35A/Chapter4/35A-4-S201.html",
        "https://le.utah.gov/xcode/Title35A/Chapter4/35A-4-S403.html",
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R994-401-202",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dwf.unemployment_insurance
        base_period_wages = person("ut_ui_base_period_wages", period)
        high_quarter_wages = person("ut_ui_high_quarter_wages", period)
        quarters_with_wages = person("ut_ui_quarters_with_wages", period)

        # § 35A-4-201(16): minimum total base-period wages.
        meets_minimum_wages = base_period_wages >= p.eligibility.min_base_period_wages
        # R994-401-202: wages in at least two base-period quarters.
        meets_quarters_test = (
            quarters_with_wages >= p.eligibility.min_quarters_with_wages
        )
        # § 35A-4-403(1)(f)(i): total base-period wages must be at least
        # 1.5 times high-quarter wages.
        meets_ratio_test = base_period_wages >= (
            p.eligibility.base_period_to_high_quarter_ratio * high_quarter_wages
        )
        return meets_minimum_wages & meets_quarters_test & meets_ratio_test
