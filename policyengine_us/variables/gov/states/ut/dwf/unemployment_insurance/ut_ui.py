from policyengine_us.model_api import *


class ut_ui(Variable):
    value_type = float
    entity = Person
    label = "Utah Unemployment Insurance"
    unit = USD
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title35A/Chapter4/35A-4-S401.html"
    defined_for = StateCode.UT
    # Annual Utah Unemployment Insurance benefit. Computed as the weekly
    # payable amount times weeks unemployed, capped at the maximum benefit
    # amount (WBA x duration) per Utah Code § 35A-4-401(4)(a).
    #
    # Not modeled (future work):
    # - REQ-023: 100% retirement income offset for pensions maintained or
    #   contributed to by a base-period employer (Utah Code
    #   § 35A-4-401(2)(c)(i)-(iii); Utah Admin Code R994-401-203). Modeling
    #   requires base-period-employer attribution that is not available in
    #   the underlying microdata.

    def formula(person, period, parameters):
        weekly_payable_amount = person("ut_ui_weekly_payable_amount", period)
        weeks_unemployed = person("ut_ui_weeks_unemployed", period)
        maximum_benefit_amount = person("ut_ui_maximum_benefit_amount", period)
        annual_benefit = weekly_payable_amount * weeks_unemployed
        return min_(annual_benefit, maximum_benefit_amount)
