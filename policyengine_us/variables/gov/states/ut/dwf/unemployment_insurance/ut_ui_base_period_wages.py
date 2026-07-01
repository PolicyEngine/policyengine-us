from policyengine_us.model_api import *


class ut_ui_base_period_wages(Variable):
    value_type = float
    entity = Person
    label = "Utah UI base period wages"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = "https://le.utah.gov/xcode/Title35A/Chapter4/35A-4-S201.html"
    # Per Utah Code § 35A-4-201(1)(a), the base period is the first four of the
    # last five completed calendar quarters preceding the first day of the
    # benefit year. Per § 35A-4-201(1)(b), claims effective on or after
    # 2011-01-02 may use the alternate base period (last four completed
    # quarters) when the standard base period fails monetary eligibility.
    # Caller should supply the more favorable of standard or alternate base
    # period wages.
