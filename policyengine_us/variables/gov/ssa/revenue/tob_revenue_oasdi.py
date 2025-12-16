from policyengine_us.model_api import *


class tob_revenue_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "OASDI trust fund revenue from SS benefit taxation (tier 1)"
    documentation = "Tax revenue from tier 1 (0-50%) Social Security benefit taxation credited to OASDI trust funds"
    unit = USD

    def formula(tax_unit, period, parameters):
        """
        Calculate OASDI trust fund revenue from tier 1 SS taxation.

        Allocates total TOB revenue to OASDI based on tier 1's proportion
        of total taxable SS.
        """
        # Get total TOB revenue
        total_tob = tax_unit("tob_revenue_total", period)

        # Get tier amounts
        tier1 = tax_unit("taxable_social_security_tier_1", period)
        tier2 = tax_unit("taxable_social_security_tier_2", period)
        total_taxable = tier1 + tier2

        # Allocate total TOB based on tier 1 proportion
        # Use where to handle division by zero
        oasdi_share = where(total_taxable > 0, tier1 / total_taxable, 0)

        return total_tob * oasdi_share
