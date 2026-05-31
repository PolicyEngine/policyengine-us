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
        snap_age_exempt = snap_work.general.age_threshold.exempted.calc(age)
        snap_non_age_exempt = person("is_snap_work_registration_exempt_non_age", period)
        general_work_compliant = person("meets_snap_general_work_requirements", period)
        abawd_work_compliant = person("meets_snap_abawd_work_requirements", period)
        hr1_in_effect = person("is_snap_abawd_hr1_in_effect", period)
        pre_hr1_abawd = parameters("2025-06-01").gov.usda.snap.work_requirements.abawd
        is_dependent = person("is_tax_unit_dependent", period)
        dependent_age_threshold = where(
            hr1_in_effect,
            snap_work.abawd.age_threshold.dependent,
            pre_hr1_abawd.age_threshold.dependent,
        )
        has_dependent_child = person.spm_unit.any(
            is_dependent & (age < dependent_age_threshold)
        )
        snap_work_compliant = where(
            has_dependent_child,
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
