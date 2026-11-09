from policyengine_us.model_api import *

# The full-time unit pays the full-time daily rate itself.
FULL_TIME_UNIT = 1


class co_ccap_care_unit(Variable):
    value_type = float
    entity = Person
    unit = "/1"
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program share of the full-time daily rate for the child's hours"
    defined_for = StateCode.CO
    reference = (
        # 8 CCR 1403-1 3.130(C), PDF page 119.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=119",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.ccap.rates
        hours = person("co_ccap_care_hours_per_day", period)
        # Without hours of care, read the full-time unit: the schedule that
        # the daily rate prices. A user who knows the hours enters them.
        return where(
            hours > 0,
            p.care_unit.calc(hours, right=True),
            FULL_TIME_UNIT,
        )
