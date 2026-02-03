from policyengine_us.model_api import *


class vt_capital_gains_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont capital gains exclusion"
    unit = USD
    documentation = (
        "Vermont offers two capital gains exclusions: a flat $5,000 exclusion for all "
        "capital gains, and a 40% exclusion (up to $350,000) only for gains from eligible "
        "assets. Stocks, bonds, financial instruments, and real estate are NOT eligible "
        "for the 40% exclusion. The exclusion is capped at 40% of federal taxable income."
    )
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-153-2024.pdf#page=1",
        "https://legislature.vermont.gov/statutes/section/32/151/05811",
    )

    def formula(tax_unit, period, parameters):
        # Get adjusted net capital gains (used for flat exclusion)
        adjusted_net_capital_gain = tax_unit(
            "adjusted_net_capital_gain", period
        )
        qualified_dividend_income = add(
            tax_unit, period, ["qualified_dividend_income"]
        )
        reduced_adjusted_net_capital_gain = max_(
            adjusted_net_capital_gain - qualified_dividend_income, 0
        )
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.exclusions.capital_gain

        # Flat $5,000 exclusion applies to ALL capital gains (including financial instruments)
        flat_exclusion = min_(reduced_adjusted_net_capital_gain, p.flat.cap)

        # 40% exclusion only applies to explicitly eligible capital gains
        # (excludes stocks, bonds, financial instruments, real estate)
        percentage_exclusion = tax_unit(
            "vt_percentage_capital_gains_exclusion", period
        )

        # Filer chooses the larger exclusion
        chosen_exclusion = max_(flat_exclusion, percentage_exclusion)

        # The chosen exclusion cannot exceed 40% of federal taxable income
        federal_taxable_income = tax_unit("taxable_income", period)
        cap = federal_taxable_income * p.income_share_cap
        return min_(chosen_exclusion, cap)
