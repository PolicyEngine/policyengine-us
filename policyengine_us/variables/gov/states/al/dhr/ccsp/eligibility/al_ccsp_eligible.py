from policyengine_us.model_api import *


class al_ccsp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alabama CCSP"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=20"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["al_ccsp_eligible_child"]) > 0
        income_eligible = spm_unit("al_ccsp_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("al_ccsp_activity_eligible", period)

        # Standard pathway: child + income + asset + activity tests.
        standard = (
            has_eligible_child & income_eligible & asset_eligible & activity_eligible
        )

        # Protective-services pathway (§2.2.2(f)) waives income and
        # activity tests. The asset test is NOT waived (State Plan
        # §2.2.6 leaves the protective-services waiver box unchecked).
        protective = spm_unit("al_ccsp_protective_services", period)
        protective_path = has_eligible_child & asset_eligible & protective

        return standard | protective_path
