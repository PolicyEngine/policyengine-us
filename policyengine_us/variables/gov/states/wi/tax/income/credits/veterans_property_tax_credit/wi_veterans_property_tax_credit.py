from policyengine_us.model_api import *


class wi_veterans_property_tax_credit(Variable):
    """Refundable credit on source-qualified municipal payments in this tax year.

    Apply the reformable rate to the full unrounded payment ledger, then round
    only the final line total half up to whole dollars. There is no income-tax
    liability cap or second cash transfer. Formula coverage starts in 2025 as a
    source-review boundary; earlier framework zeros are not legal denials.
    """

    value_type = float
    entity = TaxUnit
    label = "Wisconsin veterans and surviving spouses property tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = "wi_veterans_property_tax_credit_inputs_available"
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e",
        # PDF pages 27-30
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=27",
    )

    def formula_2025_01_01(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wi.tax.income.credits.veterans_property_tax_credit
        taxes = tax_unit(
            "wi_veterans_property_tax_credit_qualified_property_taxes", period
        )
        eligible = tax_unit("wi_veterans_property_tax_credit_eligible", period)
        rounded_credit = np.floor(taxes * p.rate + p.rounding_offset)
        return where(eligible, rounded_credit, 0)
