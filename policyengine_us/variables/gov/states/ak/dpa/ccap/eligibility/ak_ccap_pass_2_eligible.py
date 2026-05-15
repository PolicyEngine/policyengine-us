from policyengine_us.model_api import *


class ak_ccap_pass_2_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alaska CCAP PASS II (post-ATAP transitional)"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/basis/aac.asp",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=144",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ccap.eligibility
        was_recipient = spm_unit("was_atap_recipient", period.this_year)
        months_since_exit = spm_unit("months_since_atap_exit", period)
        within_window = months_since_exit < p.pass_2_transition_months
        has_eligible_child = add(spm_unit, period, ["ak_ccap_child_eligible"]) > 0
        income_eligible = spm_unit("ak_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("ak_ccap_parent_in_eligible_activity", period)
        return (
            was_recipient
            & within_window
            & has_eligible_child
            & income_eligible
            & asset_eligible
            & activity_eligible
        )
