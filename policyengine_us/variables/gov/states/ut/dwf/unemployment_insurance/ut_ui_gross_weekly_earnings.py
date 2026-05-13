from policyengine_us.model_api import *


class ut_ui_gross_weekly_earnings(Variable):
    value_type = float
    entity = Person
    label = "Utah UI gross weekly earnings while claiming"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = "https://le.utah.gov/xcode/Title35A/Chapter4/35A-4-S401.html"
    # Gross weekly earnings during a partial-unemployment week used to apply
    # the partial-benefit deduction in Utah Code § 35A-4-401(3)(a). Per
    # § 35A-4-401(3)(c), public assistance grants and similar government
    # payments are excluded from "wages" for this calculation, so the caller
    # is responsible for providing only countable earnings here (excluding
    # public assistance benefits).
