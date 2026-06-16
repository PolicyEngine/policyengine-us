from policyengine_us.model_api import *


class mn_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota CCAP based on authorized activity"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        # Minn. Stat. 142E.12, subd. 1(b) — minimum weekly hours for an
        # employed caretaker (20).
        "https://www.revisor.mn.gov/statutes/cite/142E.12",
        # Minn. Rules 3400.0040; CCAP Policy Manual 4.6.1 — activity
        # requirements based on family composition.
        "https://www.revisor.mn.gov/rules/3400.0040/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mn.dcyf.ccap.activity
        person = spm_unit.members
        is_caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        # Use the pre-labor-supply-response hours to avoid a circular
        # dependency in reform and microsimulation runs.
        hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        is_student = person("is_full_time_student", period.this_year)
        # A caretaker is in an authorized activity when employed at least the
        # minimum weekly hours or enrolled as a full-time student (education is
        # itself an authorized activity under section 4.6.6.9).
        in_activity = (hours_worked >= p.min_weekly_hours) | is_student
        # Section 4.6.1: in a two-caretaker family at least one caretaker must
        # be in an authorized activity; the other must be in an activity or
        # "unable to provide care" (a medical condition, being incapacitated or
        # institutionalized, or house arrest). is_disabled is the fallback
        # medical-condition signal.
        unable_to_provide_care = (
            person("is_disabled", period.this_year)
            | person("is_incapable_of_self_care", period.this_year)
            | person("is_incarcerated", period)
            | person("in_out_of_home_care_facility", period.this_year)
            | person("is_in_residential_care_facility", period)
        )
        no_inactive_caretaker = (
            spm_unit.sum(is_caretaker & ~in_activity & ~unable_to_provide_care) == 0
        )
        has_active_caretaker = spm_unit.sum(is_caretaker & in_activity) > 0
        # Families receiving MFIP or DWP meet the activity requirement through
        # their employment plan (section 4.6.3). The minimum-wage test and the
        # job-search, education, and training pathways are not separately
        # tracked, so the meets_ccdf_activity_test input covers them.
        on_mfip_or_dwp = spm_unit("is_tanf_enrolled", period)
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        # Section 4.6.9: families experiencing homelessness are exempt from the
        # activity requirement. We don't track the length of the exemption at the
        # moment (the manual limits it to roughly the first three months), so a
        # household flagged as homeless is treated as meeting the requirement for
        # the full period.
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        return (
            on_mfip_or_dwp
            | fallback
            | is_homeless
            | (no_inactive_caretaker & has_active_caretaker)
        )
