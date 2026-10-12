from policyengine_us.model_api import *


class ut_ui_maximum_benefit_amount(Variable):
    value_type = float
    entity = Person
    label = "Utah UI maximum benefit amount"
    unit = USD
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title35A/Chapter4/35A-4-S401.html"

    def formula(person, period, parameters):
        # § 35A-4-401(4)(a): maximum benefit amount equals the weekly benefit
        # amount times the potential duration in weeks. Returns zero when the
        # claimant is not monetarily eligible (WBA = 0 or duration = 0).
        weekly_benefit_amount = person("ut_ui_weekly_benefit_amount", period)
        duration_weeks = person("ut_ui_duration_weeks", period)
        return weekly_benefit_amount * duration_weeks
