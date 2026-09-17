from policyengine_us.model_api import *


class ma_ccfa_reimbursement_ratio(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) reimbursement ratio"
    reference = (
        "https://www.mass.gov/doc/eecfy26-rate-increase-chart/download#page=1",
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=120",
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=124",
    )
    definition_period = MONTH
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.reimbursement_rates
        childcare_hours_per_day = person("childcare_hours_per_day", period.this_year)
        # Exactly the part-time hour limit retains the lower reimbursement rate.
        part_time_ratio = p.amount_ratio.calc(childcare_hours_per_day, right=True)
        # NOTE: The part-time ratio applies to the full-time rates only. The
        # before and after school columns are partial-day rates already, and
        # only school age center-based care and the Head Start partner and
        # kindergarten table have them.
        provider_type = person("ma_ccfa_care_provider_type", period)
        provider_types = provider_type.possible_values
        age_category = person("ma_ccfa_child_age_category", period)
        schedule_type = person("ma_ccfa_schedule_type", period)
        is_school_age_center_based = (
            provider_type == provider_types.CENTER_BASED_CARE
        ) & (age_category == age_category.possible_values.SCHOOL_AGE)
        is_head_start_partner_or_kindergarten = (
            provider_type == provider_types.HEAD_START_PARTNER_AND_KINDERGARTEN
        )
        uses_before_or_after_rate = (
            schedule_type != schedule_type.possible_values.FULL_DAY
        ) & (is_school_age_center_based | is_head_start_partner_or_kindergarten)
        return where(uses_before_or_after_rate, 1, part_time_ratio)
