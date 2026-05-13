from policyengine_us.model_api import *


class ut_ui_weeks_unemployed(Variable):
    value_type = int
    entity = Person
    label = "Utah UI weeks unemployed"
    unit = "week"
    definition_period = YEAR
    default_value = 0
    reference = "https://le.utah.gov/xcode/Title35A/Chapter4/35A-4-S401.html"
    # Number of weeks during the year the claimant collected (or would
    # collect) Utah Unemployment Insurance benefits. Used to convert the
    # weekly payable amount into an annual benefit, capped by the maximum
    # benefit amount per Utah Code § 35A-4-401(4)(a).
