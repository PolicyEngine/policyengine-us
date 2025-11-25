from policyengine_us.model_api import *


class tob_revenue_medicare_hi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Medicare HI trust fund revenue from SS benefit taxation (tier 2)"
    documentation = "Tax revenue from tier 2 (50-85%) Social Security benefit taxation credited to Medicare HI trust fund"
    unit = USD

    def formula(tax_unit, period, parameters):
        """
        Calculate Medicare HI trust fund revenue from tier 2 SS taxation.

        Allocates total TOB revenue to Medicare HI based on tier 2's proportion
        of total taxable SS.
        """
        # Get total TOB revenue
        total_tob = tax_unit("tob_revenue_total", period)

        # Get tier amounts
        tier1 = tax_unit("taxable_social_security_tier_1", period)
        tier2 = tax_unit("taxable_social_security_tier_2", period)
        total_taxable = tier1 + tier2

        # Allocate total TOB based on tier 2 proportion
        # Use np.divide with out/where to handle division by zero safely
        medicare_share = np.divide(
            tier2,
            total_taxable,
            out=np.zeros_like(tier2, dtype=np.float32),
            where=total_taxable != 0,
        )

        return total_tob * medicare_share
