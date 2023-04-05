from policyengine_us.model_api import *


class ny_tanf_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York TANF asset eligible"
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(spm_unit, period, parameters):
        # The amount of assets that a family may own and qualify for FA is $2,000
        # except for households in which any member is age 60 or over in which case $3,000 in assets can be owned.
        # https://otda.ny.gov/policy/tanf/TANF-State-Plan-2021-2023.pdf#page=7, #10
        is_any_family_members_over_60 = spm_unit(
            "is_any_family_members_over_60", period
        )
        amount_of_asset = spm_unit("amount_of_asset", period)
        return amount_of_asset <= where(
            is_any_family_members_over_60, 3000, 2000
        )
