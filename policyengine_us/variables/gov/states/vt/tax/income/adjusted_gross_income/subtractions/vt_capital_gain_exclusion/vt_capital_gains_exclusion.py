from policyengine_us.model_api import *


class vt_capital_gains_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont capital gains exclusion"
    unit = USD
    documentation = "Vermont excludes a portion of capital gains, calculated either as a flat amount or as a fraction of adjusted net capital gains, and limited by a fraction of federal taxable income."
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-153-2022.pdf#page=1"  # 2022 Schedule IN-153 Vermont Capital Gains Exclusion Calculation
        "https://legislature.vermont.gov/statutes/section/32/151/05811"  # Titl. 32 V.S.A. § 5811(21)(B)(ii)
        "https://tax.vermont.gov/sites/tax/files/documents/IN-153%20Instr-2022.pdf"
    )

    def formula(tax_unit, period, parameters):
        # Get adjusted net capital gains, which is capped at 0
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
        # The flat exclusion is the less of a capped amount
        # or the actual amount of net adjusted capital gains
        flat_exclusion = min_(reduced_adjusted_net_capital_gain, p.flat.cap)
        # Get percentage exclusion
        percentage_exclusion = tax_unit(
            "vt_percentage_capital_gains_exclusion", period
        )
        # Filer can choose from flat or percentage exclusion.
        # Assume the filer will always choose the larger one
        chosen_exclusion = max_(flat_exclusion, percentage_exclusion)
        # The chosen exclusion should not exceed 40% of federal taxable income
        federal_taxable_income = tax_unit("taxable_income", period)
        cap = federal_taxable_income * p.income_share_cap
        return min_(chosen_exclusion, cap)
