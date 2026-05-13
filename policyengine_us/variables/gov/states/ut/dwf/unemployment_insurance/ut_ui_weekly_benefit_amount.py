from policyengine_us.model_api import *


class ut_ui_weekly_benefit_amount(Variable):
    value_type = float
    entity = Person
    label = "Utah UI weekly benefit amount"
    unit = USD
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title35A/Chapter4/35A-4-S401.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dwf.unemployment_insurance
        high_quarter_wages = person("ut_ui_high_quarter_wages", period)
        monetarily_eligible = person("ut_ui_monetarily_eligible", period)

        # § 35A-4-401(2)(a)(ii): WBA = floor(high quarter wages / 26) - $5.
        # Utah has no statutory minimum WBA, so the raw amount is floored at
        # zero rather than at a positive minimum.
        raw_wba = (
            np.floor(high_quarter_wages / p.benefit.wba.divisor)
            - p.benefit.wba.subtraction
        )
        # § 35A-4-401(2)(b)(ii): WBA is capped at the annual maximum.
        capped_wba = min_(max_(raw_wba, 0), p.benefit.wba.max_amount)
        # Zero out when the claimant is not monetarily eligible.
        return capped_wba * monetarily_eligible
