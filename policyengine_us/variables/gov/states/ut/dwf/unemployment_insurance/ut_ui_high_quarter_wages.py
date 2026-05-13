from policyengine_us.model_api import *


class ut_ui_high_quarter_wages(Variable):
    value_type = float
    entity = Person
    label = "Utah UI high quarter wages"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = "https://le.utah.gov/xcode/Title35A/Chapter4/35A-4-S201.html"
    # Wages paid during the calendar quarter of the base period in which the
    # claimant's wages were highest, used to compute the weekly benefit amount
    # under Utah Code § 35A-4-401(2)(a)(ii).
