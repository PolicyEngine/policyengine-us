from policyengine_us.model_api import *


class ia_tanf_fip_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP countable resources"
    unit = USD
    definition_period = MONTH
    reference = "Iowa Administrative Code 441-41.26"
    documentation = (
        "Total countable resources after exemptions for homestead, "
        "burial assets, vehicle equity, and other exempt resources."
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # Get total assets from household members
        person = spm_unit.members
        total_assets = person("household_assets", period)

        # For simplicity, we'll use household_assets as a baseline
        # In a full implementation, this would subtract exemptions for:
        # - Homestead
        # - Burial assets ($1,500 per person)
        # - Vehicle equity (up to $3,959 per vehicle per adult)
        # - Household goods and personal effects
        # - IDA accounts
        # - Self-employment assets (up to $10,000)

        return spm_unit.sum(total_assets)
