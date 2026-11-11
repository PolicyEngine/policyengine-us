from policyengine_us.model_api import *

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
        "child in grades 1 to 12 (section 3.124(W)). The model also reads a "
        "child in grades 1 to 12 whose only reported care is an after-school "
        "expense as in part-time care. Care schedules do not change within a "
        "year here, so the majority-of-months rule in section 3.124(V) gives "
        "the same answer."
    )
    reference = (
        # PDF pages 10, 85, 119
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=10",
    )
    definition_period = MONTH
    defined_for = "co_ccap_child_in_care"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.ccap.parent_fee.part_time
        units = person("co_ccap_full_time_equivalent_units", period)
        # The units come from values stored in single precision, which can put
        # an exact 13 units a hair below the threshold; four decimals clear it.
        part_time_units = np.round(units, 4) < p.unit_threshold
        year = period.this_year
        # co_ccap_care_unit reads the part-time unit for a child whose only
        # care comes after school (co_ccap_after_school_care_only).
        part_time_days = person("co_ccap_care_unit", period) < 1
        in_grade_one_or_above = person("is_in_k12_school", year) & (
            person("age", year) >= FIRST_GRADE_AGE
        )
        return part_time_units | (in_grade_one_or_above & part_time_days)
