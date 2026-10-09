from policyengine_us.model_api import *


class wi_retirement_income_exclusion_elected(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Wisconsin retirement income exclusion is elected"
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/d",
        "https://docs.legis.wisconsin.gov/2025/related/acts/174.pdf#page=2",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=7",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income
        if not p.subtractions.retirement_income.exclusion.in_effect:
            return tax_unit.filled_array(False)

        # Compare net tax on each return before publishing the elected path.
        # Reading the credit components avoids a cycle through the reported
        # before-refundable tax and refundable credits.
        standard_before_refundable = max_(
            0,
            tax_unit("wi_income_tax_before_credits", period)
            - tax_unit("wi_non_refundable_credits", period),
        )
        standard_refundable = add(tax_unit, period, p.credits.refundable)
        exclusion_refundable = add(
            tax_unit, period, p.credits.retirement_income_exclusion_refundable
        )
        exclusion_net = (
            tax_unit("wi_retirement_income_exclusion_tax", period)
            - exclusion_refundable
        )
        standard_net = standard_before_refundable - standard_refundable
        line16 = tax_unit("wi_retirement_income_exclusion_amount", period)
        # Keep the standard path on a tie and require qualifying income.
        return (line16 > 0) & (exclusion_net < standard_net)
