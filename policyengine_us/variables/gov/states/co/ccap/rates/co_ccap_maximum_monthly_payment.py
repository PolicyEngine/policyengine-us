from policyengine_us.model_api import *


class co_ccap_maximum_monthly_payment(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program county rate for the child's care in a month"
    defined_for = "co_ccap_child_eligible"
    reference = (
        # 8 CCR 1403-1 3.125(FFF), PDF page 101.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=101",
        # 3.130(C), PDF page 119.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=119",
    )

    def formula(person, period, parameters):
        daily_rate = person("co_ccap_daily_rate", period)
        days = person("co_ccap_care_days_per_month", period)
        return daily_rate * days
