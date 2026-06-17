from policyengine_us.model_api import *


class ms_ccpp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Mississippi CCPP"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=25"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["ms_ccpp_eligible_child"]) > 0
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        income_eligible = spm_unit("ms_ccpp_income_eligible", period)
        activity_eligible = spm_unit("ms_ccpp_activity_eligible", period)

        # Standard low-income pathway: eligible child, assets, income, and a
        # qualifying parent activity.
        standard = (
            has_eligible_child & asset_eligible & income_eligible & activity_eligible
        )

        # Categorical pathways (TANF, homeless, protective services) bypass the
        # income and activity tests; the eligible child and asset tests still
        # apply.
        categorical = spm_unit("ms_ccpp_categorically_eligible", period)
        categorical_path = has_eligible_child & asset_eligible & categorical

        return standard | categorical_path
