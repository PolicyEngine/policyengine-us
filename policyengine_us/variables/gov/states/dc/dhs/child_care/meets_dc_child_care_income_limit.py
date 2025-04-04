from policyengine_us.model_api import *


class meets_dc_child_care_income_limit(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets DC Childcare Subsidy income limits"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf"

    def formula(spm_unit, period, parameters):
        # Get income limit parameters
        p = parameters(period).gov.states.dc.dhs.child_care

        # Get countable income
        countable_income = spm_unit("dc_child_care_countable_income", period)

        # Calculate FPL for the household
        fpg = spm_unit("tax_unit_fpg", period)

        # Initial eligibility - 300% FPL
        initial_fpg_limit = p.initial_eligibility_fpg_percent

        # Redetermination would use SMI but we'll use FPL as a proxy for now
        # In a full implementation, we would check SMI for continuing eligibility

        # Check if income is below initial eligibility limit
        meets_fpg_limit = countable_income <= (fpg * initial_fpg_limit / 100)

        # Check asset limit - this is simplified as we don't have detailed asset variables
        # In a real implementation, we would sum all relevant assets
        # assets = spm_unit("total_assets", period)
        # meets_asset_limit = assets <= p.asset_limit
        meets_asset_limit = True  # Simplified for now

        return meets_fpg_limit & meets_asset_limit
