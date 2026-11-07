from policyengine_us.model_api import *


class ga_caps_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Georgia CAPS"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=29",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["ga_caps_eligible_child"]) > 0
        income_eligible = spm_unit("ga_caps_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("ga_caps_activity_eligible", period)
        # CAPS/00-7, 7.3.1: new applicants outside a priority group are denied even
        # when they meet every other requirement. 7.3.1.3 drops the requirement at
        # annual redetermination.
        priority_group_met = spm_unit(
            "ga_caps_priority_group_eligible", period
        ) | spm_unit("ga_caps_enrolled", period)
        return (
            has_eligible_child
            & income_eligible
            & asset_eligible
            & activity_eligible
            & priority_group_met
        )
