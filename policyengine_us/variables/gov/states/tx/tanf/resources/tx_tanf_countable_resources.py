from policyengine_us.model_api import *


class tx_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF countable resources"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1210-general-policy",
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1220-limits",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Get all resource types
        # Using cash_assets which includes checking and savings
        cash_assets = spm_unit("spm_unit_cash_assets", period.this_year)

        # Convert annual to monthly
        monthly_cash_assets = cash_assets / MONTHS_IN_YEAR

        # Get vehicle values
        # Note: Using simplified approach - full implementation would track individual vehicles
        vehicle_assets = (
            spm_unit("spm_unit_vehicle_net_value", period.this_year)
            / MONTHS_IN_YEAR
        )

        # Apply vehicle exemptions
        p = parameters(period).gov.states.tx.tanf.resources
        primary_exemption = p.vehicle_exemption_primary

        # Simplified: Apply primary vehicle exemption
        countable_vehicle_value = max_(vehicle_assets - primary_exemption, 0)

        # Sum all countable resources
        total_resources = monthly_cash_assets + countable_vehicle_value

        return total_resources
