from policyengine_us.model_api import *


class wa_pfml(Variable):
    value_type = float
    entity = Person
    label = "Washington PFML benefit"
    documentation = (
        "Annual Washington Paid Family and Medical Leave benefit. "
        "Computed as the weekly benefit amount multiplied by the "
        "claimed leave weeks, capped at the maximum duration for the "
        "selected leave type."
    )
    unit = USD
    definition_period = YEAR
    defined_for = "wa_pfml_eligible"
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020",
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.010",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.pfml
        weekly_benefit = person("wa_pfml_weekly_benefit_amount", period)
        leave_type = person("wa_pfml_leave_type", period)
        leave_type_values = leave_type.possible_values
        max_leave_weeks = select(
            [
                leave_type == leave_type_values.FAMILY,
                leave_type == leave_type_values.MEDICAL,
                leave_type == leave_type_values.COMBINED,
                leave_type == leave_type_values.MEDICAL_WITH_PREGNANCY_INCAPACITY,
                leave_type == leave_type_values.COMBINED_WITH_PREGNANCY_INCAPACITY,
            ],
            [
                p.duration.family_leave_weeks,
                p.duration.medical_leave_weeks,
                p.duration.combined_max_weeks,
                p.duration.medical_leave_weeks_with_pregnancy_incapacity,
                p.duration.combined_max_weeks_with_pregnancy_incapacity,
            ],
            default=0,
        )
        leave_hours_claimed = np.floor(person("wa_pfml_leave_hours_claimed", period))
        typical_workweek_hours = person("wa_pfml_typical_workweek_hours", period)
        leave_hours_meet_minimum = where(
            leave_hours_claimed >= p.min_claim_hours,
            leave_hours_claimed,
            0,
        )
        leave_weeks_from_hours = np.divide(
            clip(
                leave_hours_meet_minimum,
                0,
                max_leave_weeks * typical_workweek_hours,
            ),
            typical_workweek_hours,
            out=np.zeros_like(leave_hours_meet_minimum, dtype=np.float32),
            where=typical_workweek_hours > 0,
        )
        leave_weeks_from_weeks = clip(
            person("wa_pfml_leave_weeks", period),
            0,
            max_leave_weeks,
        )
        leave_weeks = where(
            (leave_hours_claimed > 0) & (typical_workweek_hours > 0),
            leave_weeks_from_hours,
            leave_weeks_from_weeks,
        )
        return weekly_benefit * leave_weeks
