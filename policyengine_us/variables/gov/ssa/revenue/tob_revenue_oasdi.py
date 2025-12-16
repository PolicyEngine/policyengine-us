from policyengine_us.model_api import *


class tob_revenue_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "OASDI trust fund revenue from SS benefit taxation"
    documentation = (
        "Tax revenue from Social Security benefit taxation credited to OASDI trust funds. "
        "Per IRC §86(d)(2), tax on the 'first 50 percent' of gross SS benefits goes to OASDI."
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/86#d_2"

    def formula(tax_unit, period, parameters):
        """
        Calculate OASDI trust fund revenue per IRC §86(d)(2).

        The statute allocates revenue based on 'the first 50 percent of
        the social security benefits received' - meaning 50% of gross benefits,
        not the IRC §86 tier amounts (which have a bracket cap).

        OASDI receives: tax on min(taxable_ss, 50% × gross_ss)
        """
        # Get total TOB revenue
        total_tob = tax_unit("tob_revenue_total", period)

        # Get gross and taxable SS amounts
        gross_ss = tax_unit("tax_unit_social_security", period)
        taxable_ss = tax_unit("tax_unit_taxable_social_security", period)

        # Per IRC §86(d)(2): OASDI gets tax on "first 50%" of gross benefits
        # The 50% rate is the base benefit cap from IRC §86(a)(1)(A)
        p = parameters(period).gov.irs.social_security.taxability.rate.base
        oasdi_taxable_portion = min_(taxable_ss, p.benefit_cap * gross_ss)

        # Calculate OASDI's share of total TOB revenue
        oasdi_share = where(
            taxable_ss > 0, oasdi_taxable_portion / taxable_ss, 0
        )

        return total_tob * oasdi_share
