from policyengine_us.model_api import *


class ma_eaedc_assets_limit_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Assets limit eligible for the Massachusetts EAEDC"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-110"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.assets
        countable_assets = spm_unit("ma_eaedc_countable_assets", period)
        living_arrangement = spm_unit("ma_eaedc_living_arrangement", period)

        living_arrangement_E = (
            living_arrangement == living_arrangement.possible_values.E
        )
        asset_below_limit = countable_assets <= p.limit
        # Only living arrangement E has an asset limit

        return (
            living_arrangement_E & asset_below_limit
        ) | ~living_arrangement_E
