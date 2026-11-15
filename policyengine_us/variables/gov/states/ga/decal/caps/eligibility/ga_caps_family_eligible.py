from policyengine_us.model_api import *


class ga_caps_family_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Georgia CAPS as a family, apart from children in DFCS custody"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        # PDF pages 27, 29
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=27",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=1",
        "https://caps.decal.ga.gov/Assets/downloads/CAPS_Letter_from_Elisabetta_Kasfir_Families_07.01.2024.pdf#page=1",
        "https://caps.decal.ga.gov/Assets/downloads/CAPS_Letter_to_Families_Policy_Revisions_10.06.25.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.priority_groups
        person = spm_unit.members
        # CAPS/00-5, 5.4.1: a child in DFCS custody forms a family unit of one, so
        # the family's own case covers its other children.
        family_child = person("ga_caps_eligible_child", period) & ~person(
            "is_in_foster_care", period
        )
        has_eligible_child = spm_unit.any(family_child)
        income_eligible = spm_unit("ga_caps_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("ga_caps_activity_eligible", period)
        # CAPS/00-7, 7.3.1: new applicants outside a priority group are denied even
        # when they meet every other requirement. 7.3.1.3 drops the requirement at
        # annual redetermination. From July 1, 2024 to October 6, 2025, a family whose
        # child attended Georgia's Pre-K at the initial application or the previous
        # determination had to belong to a group at redetermination.
        pre_k_family = spm_unit.any(
            person("ga_caps_pre_k_at_previous_determination", period)
        )
        exempt_at_redetermination = spm_unit("ga_caps_enrolled", period) & ~(
            pre_k_family & p.pre_k_redetermination_in_effect
        )
        priority_group_met = (
            spm_unit("ga_caps_priority_group_eligible", period)
            | exempt_at_redetermination
        )
        return (
            has_eligible_child
            & income_eligible
            & asset_eligible
            & activity_eligible
            & priority_group_met
        )
