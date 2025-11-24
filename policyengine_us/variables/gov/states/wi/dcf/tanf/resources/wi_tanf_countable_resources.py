from policyengine_us.model_api import *


class wi_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wisconsin TANF countable resources"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/"
        "03.3.4_COUNTING_ASSETS.htm",
    )
    defined_for = StateCode.WI
    documentation = """
    Wisconsin W-2 counts assets (combined equity value) with exclusions:
    - First $10,000 of vehicle equity is excluded
    - One primary residence excluded (if under 200% median home value)
    - Household goods and personal effects excluded
    - IDA match funds excluded
    - Federal income tax refunds excluded for 12 months

    For simplified implementation, we use available asset data and apply
    the vehicle exclusion.
    """

    def formula(spm_unit, period, parameters):
        # Use available household assets
        # Access household net worth from SPMUnit level
        total_assets = spm_unit.household("net_worth", period)

        # Apply vehicle equity exclusion
        p = parameters(period).gov.states.wi.dcf.tanf.asset_limit
        vehicle_exclusion = p.vehicle_exclusion

        # Simplified calculation: apply vehicle exclusion to total assets
        # NOTE: Ideally we would separate vehicle equity from other assets,
        # but this data is not available in standard microdata
        return max_(total_assets - vehicle_exclusion, 0)
