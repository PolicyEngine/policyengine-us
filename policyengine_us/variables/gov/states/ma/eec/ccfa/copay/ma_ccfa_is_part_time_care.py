from policyengine_us.model_api import *


class ma_ccfa_is_part_time_care(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Massachusetts CCFA child receives part-time care"
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=76",
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=120",
        "https://www.mass.gov/doc/eecfy26-rate-increase-chart/download#page=1",
        "https://www.mass.gov/doc/eec-policy-advisory-field-operations-2024-6-ccfa-enrollment-and-attendance-codes/download#page=3",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.copay
        daily_hours = person("childcare_hours_per_day", period.this_year)
        short_day = (daily_hours > 0) & (daily_hours <= p.maximum_part_time_daily_hours)
        # The rate chart prices before and after school care as part-day rates
        # for school age center-based care and for the Head Start partner and
        # kindergarten table, and school age family child care is paid the
        # part-day rate on school days. The sources give a before or after
        # school schedule no meaning for other children, so it is ignored.
        # Keep in step with reimbursement/ma_ccfa_reimbursement_ratio.py.
        schedule = person("ma_ccfa_schedule_type", period)
        is_before_or_after = schedule != schedule.possible_values.FULL_DAY
        provider_type = person("ma_ccfa_care_provider_type", period)
        provider_types = provider_type.possible_values
        age_category = person("ma_ccfa_child_age_category", period)
        is_school_age = age_category == age_category.possible_values.SCHOOL_AGE
        is_school_age_center_or_family = is_school_age & (
            (provider_type == provider_types.CENTER_BASED_CARE)
            | (provider_type == provider_types.FAMILY_CHILD_CARE)
        )
        is_head_start_partner_or_kindergarten = (
            provider_type == provider_types.HEAD_START_PARTNER_AND_KINDERGARTEN
        )
        has_part_day_schedule = is_before_or_after & (
            is_school_age_center_or_family | is_head_start_partner_or_kindergarten
        )
        return short_day | has_part_day_schedule
