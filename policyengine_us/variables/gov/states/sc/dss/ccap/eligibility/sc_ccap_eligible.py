from policyengine_us.model_api import *


class sc_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for South Carolina CCAP"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=14",
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=65",
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=91",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["sc_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("sc_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("sc_ccap_activity_eligible", period)

        # Standard non-welfare low-income pathway (Section 2.13).
        standard = (
            has_eligible_child & income_eligible & asset_eligible & activity_eligible
        )

        # Protective services pathway (Section 2.4) — waives copay and
        # activity. Section 2.4 does not explicitly waive income; families
        # are still subject to the 85% SMI income test.
        protective = spm_unit("sc_ccap_protective_services", period)
        protective_path = (
            has_eligible_child & income_eligible & asset_eligible & protective
        )

        # Head Start wraparound pathway (Section 2.15) — waives income
        # and activity.  The Head Start child itself must be CCDF-eligible
        # (age + immigration); a sibling's eligibility cannot combine with
        # a different child's Head Start enrollment.
        person = spm_unit.members
        head_start_eligible_child = person("sc_ccap_eligible_child", period) & person(
            "is_enrolled_in_head_start", period.this_year
        )
        has_head_start_eligible_child = spm_unit.any(head_start_eligible_child)
        head_start_path = has_head_start_eligible_child & asset_eligible

        return standard | protective_path | head_start_path
