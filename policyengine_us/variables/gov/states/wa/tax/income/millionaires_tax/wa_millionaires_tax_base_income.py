from policyengine_us.model_api import *


class wa_millionaires_tax_base_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington millionaires tax base income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=7",
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=11",
    )
    defined_for = "wa_millionaires_tax_applies"

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        long_term_capital_gains = add(tax_unit, period, ["long_term_capital_gains"])
        tax_exempt_interest = add(tax_unit, period, ["tax_exempt_interest_income"])

        p = parameters(period).gov.states.wa.tax.income.capital_gains
        charitable_contributions = add(
            tax_unit,
            period,
            ["charitable_cash_donations", "charitable_non_cash_donations"],
        )
        charitable_contributions_above_exemption = max_(
            0, charitable_contributions - p.deductions.charitable.exemption
        )
        charitable_deduction = min_(
            charitable_contributions_above_exemption,
            p.deductions.charitable.cap,
        )
        washington_capital_gains = max_(
            0, long_term_capital_gains - charitable_deduction
        )
        owes_washington_capital_gains_tax = tax_unit("wa_capital_gains_tax", period) > 0

        return (
            agi
            - long_term_capital_gains
            + tax_exempt_interest
            + washington_capital_gains * owes_washington_capital_gains_tax
        )
