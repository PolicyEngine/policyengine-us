from policyengine_us.model_api import *


class medicaid_community_engagement_pass_through_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid community engagement pass-through eligibility"
    definition_period = MONTH
    documentation = (
        "Under 42 CFR 435.554(c)(7) (CMS-2454-IFC), the SNAP exclusion from "
        "the Medicaid community engagement requirement is a status test: the "
        "individual is a member of a household receiving SNAP and is not "
        "exempt from (i.e., is subject to) a SNAP work requirement. Unlike "
        "the TANF exclusion, states do not confirm actual compliance with "
        "SNAP work requirements. The model tests subject-to status with the "
        "general work requirement age brackets and non-age registration "
        "exemptions; the 7 CFR 273.7(b)(1)(vii) exemption for people working "
        "30 or more hours weekly is not netted out, and post-HR1 adults aged "
        "60-64 who are subject only to the ABAWD requirement are not "
        "separately captured."
    )
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib12082025.pdf#page=6",
        "https://www.federalregister.gov/documents/2026/06/03/2026-11094/medicaid-program-community-engagement-requirement-for-certain-individuals",
        "https://www.ecfr.gov/current/title-42/part-435/section-435.554#p-435.554(c)(7)",
    )

    def formula(person, period, parameters):
        snap_work = parameters(period).gov.usda.snap.work_requirements
        snap = (person.spm_unit("snap", period) > 0) | person.spm_unit(
            "receives_snap", period
        )
        tanf = person.spm_unit("is_tanf_enrolled", period) | person.spm_unit(
            "receives_tanf", period
        )

        age = person("monthly_age", period)
        # Cast to bool: single_amount bool brackets return int (0/1), which
        # would make the ~ below a bitwise negation instead of a logical one.
        snap_age_exempt = snap_work.general.age_threshold.exempted.calc(age).astype(
            bool
        )
        snap_non_age_exempt = person("is_snap_work_registration_exempt_non_age", period)
        snap_pass_through = snap & ~snap_age_exempt & ~snap_non_age_exempt

        tanf_pass_through = tanf & person.spm_unit(
            "meets_tanf_work_requirements", period
        )
        return snap_pass_through | tanf_pass_through
