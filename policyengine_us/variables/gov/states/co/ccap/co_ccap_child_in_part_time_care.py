from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_parameter_instant import (
    co_ccap_parameter_instant,
)

# PolicyEngine has no school grade input, so a child in school aged 6 or older
# is taken to be in grade 1 or above. This is an imputation, not a rule, so it
# is not a parameter.
FIRST_GRADE_AGE = 6


class co_ccap_child_in_part_time_care(Variable):
    value_type = bool
    entity = Person
    label = "Child in part-time care for the Colorado Child Care Assistance Program parent fee"
    documentation = (
        "Care averaging fewer than 13 full-time equivalent units a month is part "
        "time (section 3.124(U)), and so is care of up to 5 hours a day for a "
        "child in grades 1 to 12 (section 3.124(W)). Care schedules do not "
        "change within a year here, so the majority-of-months rule in section "
        "3.124(V) gives the same answer."
    )
    reference = (
        # PDF pages 10, 85, 119
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=10",
    )
    definition_period = MONTH
    defined_for = "co_ccap_child_in_care"

    def formula(person, period, parameters):
        instant_str = co_ccap_parameter_instant(period)
        p = parameters(instant_str).gov.states.co.ccap.parent_fee.part_time
        units = person("co_ccap_full_time_equivalent_units", period)
        part_time_units = units < p.unit_threshold
        year = period.this_year
        daily_hours = person("childcare_hours_per_day", year)
        part_time_days = (daily_hours > 0) & (
            p.full_time_equivalent_units.calc(daily_hours, right=True) < 1
        )
        in_grade_one_or_above = person("is_in_k12_school", year) & (
            person("age", year) >= FIRST_GRADE_AGE
        )
        return part_time_units | (in_grade_one_or_above & part_time_days)
