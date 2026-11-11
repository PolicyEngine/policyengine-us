from policyengine_us.model_api import *


class co_ccap_full_time_equivalent_units(Variable):
    value_type = float
    entity = Person
    label = "Colorado Child Care Assistance Program full-time equivalent units of care per month"
    documentation = (
        "A child's monthly units of care, with each part-time unit counted as "
        "0.55 of a full-time unit. A day of care of unknown length counts as "
        "one full-time unit. Days of care come from the larger of the weekly "
        "schedule (days a week times 52 / 12) and attending days a month, and "
        "a child with neither attends each weekday."
    )
    reference = (
        # 8 CCR 1403-1 3.103(ZZ), 3.124(U) and (V), and 3.130(C) and (F), PDF
        # pages 10, 85 and 119-120: full-time equivalent units, part-time
        # fees, daily units and drop-in days.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=10",
    )
    definition_period = MONTH
    defined_for = "co_ccap_child_in_care"

    def formula(person, period, parameters):
        # Counties assess the fee on the authorized care schedule (3.124(V)).
        unit = person("co_ccap_care_unit", period)
        days = person("co_ccap_care_days_per_month", period)
        return unit * days
