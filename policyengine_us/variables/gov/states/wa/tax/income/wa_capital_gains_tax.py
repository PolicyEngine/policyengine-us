from policyengine_us.model_api import *


class wa_capital_gains_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington capital gains tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA

    def formula(tax_unit, period, parameters):
        in_effect = parameters(period).gov.states.wa.tax.income.in_effect
        if in_effect:
            p = parameters(period).gov.states.wa.tax.income.capital_gains
            ltcg = add(tax_unit, period, ["long_term_capital_gains"])
            # Deduct charitable contributions.
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
            # Get base after standard and charitable deductions.
            taxable_ltcg = max_(
                0, ltcg - charitable_deduction - p.deductions.standard
            )
            return taxable_ltcg * p.rate
        return 0
