from policyengine_us.model_api import *


class medicaid_community_engagement_pass_through_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid community engagement pass-through eligibility"
    definition_period = MONTH
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib12082025.pdf#page=6",
    )

    def formula(person, period, parameters):
        snap_work = parameters(period).gov.usda.snap.work_requirements
        snap = person.spm_unit("snap", period) > 0
        tanf = person.spm_unit("is_tanf_enrolled", period)

        age = person("monthly_age", period)
        # Cast to bool: single_amount bool brackets return int (0/1), which
        # would make the ~ below a bitwise negation instead of a logical one.
        snap_age_exempt = snap_work.general.age_threshold.exempted.calc(age).astype(
            bool
        )
        snap_non_age_exempt = person("is_snap_work_registration_exempt_non_age", period)
        general_work_compliant = person("meets_snap_general_work_requirements", period)
        abawd_work_compliant = person("meets_snap_abawd_work_requirements", period)
        hr1_in_effect = person("is_snap_abawd_hr1_in_effect", period)
        pre_hr1_abawd = parameters("2025-06-01").gov.usda.snap.work_requirements.abawd
        dependent_age_threshold = where(
            hr1_in_effect,
            snap_work.abawd.age_threshold.dependent,
            pre_hr1_abawd.age_threshold.dependent,
        )
        # Mirror the SNAP ABAWD child exception exactly: 7 CFR 273.24(c)(4)
        # keys on any household member under the age threshold, regardless of
        # tax-unit dependency (see meets_snap_work_requirements_person). The
        # pass-through deems a person compliant because they satisfy SNAP's
        # requirements, so it must apply SNAP's own exception semantics.
        has_household_child = person.spm_unit.any(age < dependent_age_threshold)
        snap_work_compliant = where(
            has_household_child,
            general_work_compliant,
            general_work_compliant & abawd_work_compliant,
        )
        snap_pass_through = (
            snap & ~snap_age_exempt & ~snap_non_age_exempt & snap_work_compliant
        )

        tanf_pass_through = tanf & person.spm_unit(
            "meets_tanf_work_requirements", period
        )
        return snap_pass_through | tanf_pass_through
