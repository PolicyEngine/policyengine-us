from policyengine_us.model_api import *


class capital_gains_excluded_from_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capital gains excluded from taxable income"
    unit = USD
    documentation = "This is subtracted from taxable income (plus any section 911 exclusion) before applying the ordinary tax rates. Capital gains tax is calculated separately."
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(1)(A)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_1_A",
        ),
        dict(
            title="26 U.S. Code § 911(f)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f",
        ),
    ]

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.capital_gains
        # A taxpayer excluding foreign earned income applies section 1(h) to
        # taxable income plus the excluded amount, with gains reduced by any
        # capital gain excess (26 U.S.C. 911(f)). Everyone else's amounts are
        # unchanged.
        net_capital_gain = tax_unit("section_911_net_capital_gain", period)
        adjusted_net_capital_gain = tax_unit(
            "section_911_adjusted_net_capital_gain", period
        )
        taxable_income = tax_unit("taxable_income_plus_section_911_exclusion", period)
        filing_status = tax_unit("filing_status", period)
        income_taxed_below_first_rate = clip(
            taxable_income, 0, p.thresholds["1"][filing_status]
        )
        reduced_taxable_income = max_(
            taxable_income - net_capital_gain,
            min_(
                income_taxed_below_first_rate,
                taxable_income - adjusted_net_capital_gain,
            ),
        )
        return taxable_income - reduced_taxable_income
