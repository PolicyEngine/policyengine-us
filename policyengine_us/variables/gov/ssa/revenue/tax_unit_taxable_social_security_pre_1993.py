from policyengine_us.model_api import *


class tax_unit_taxable_social_security_pre_1993(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Social Security benefits includible under pre-1993 section 86"
    documentation = (
        "Counterfactual Social Security inclusion under section 86 before the "
        "1993 amendments, used to allocate taxation-of-benefits revenue to OASDI. "
        "The original law limits inclusion to half of benefits and half of "
        "provisional income above the unindexed base amount."
    )
    unit = USD
    reference = (
        "https://tile.loc.gov/storage-services/service/ll/uscode/uscode1988-01002/uscode1988-010026001/uscode1988-010026001.pdf#page=240",
        "https://www.ssa.gov/OP_Home/comp2/F098-021.html",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.ssa.revenue.pre_1993
        benefits = tax_unit("tax_unit_social_security_for_taxability", period)
        # Section 86(b) also used one-half of benefits in provisional income.
        # Keep the historical counterfactual independent of current-law rates.
        combined_income = tax_unit("taxable_ss_magi", period) + p.rate * benefits
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        cohabitating = tax_unit("cohabitating_spouses", period)
        base_amount = where(
            separate & cohabitating,
            p.base_amount.separate_cohabitating,
            p.base_amount.main[filing_status],
        )
        excess = max_(combined_income - base_amount, 0)
        return p.rate * min_(benefits, excess)
