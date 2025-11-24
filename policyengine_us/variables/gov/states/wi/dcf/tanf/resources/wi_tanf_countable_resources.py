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
        # Get liquid assets (cash, checking, savings, stocks) - excludes vehicles
        liquid_assets = spm_unit("spm_unit_cash_assets", period)

        # Get vehicle value separately
        vehicle_value = spm_unit.household("household_vehicles_value", period)

        # Apply vehicle equity exclusion ($10,000 excluded)
        p = parameters(period).gov.states.wi.dcf.tanf.asset_limit
        countable_vehicle = max_(vehicle_value - p.vehicle_exclusion, 0)

        # Total countable resources = liquid assets + countable vehicles
        # Note: Home equity is excluded in Wisconsin's rules
        return liquid_assets + countable_vehicle
