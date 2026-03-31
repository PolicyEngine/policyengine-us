from policyengine_us.model_api import *


class wa_millionaires_tax_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington millionaires tax taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=5",
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=12",
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=13",
    )
    defined_for = StateCode.WA
    documentation = """
    Washington taxable income is Washington base income minus the standard
    deduction ($1,000,000) and charitable contribution deduction (up to $100,000).

    Per Sec. 101(12), Washington taxable income is "Washington base income as
    further modified by sections 309 through 314."
    """

    def formula(tax_unit, period, parameters):
        in_effect = parameters(
            period
        ).gov.states.wa.tax.income.millionaires_tax.in_effect
        base_income = tax_unit("wa_millionaires_tax_base_income", period)
        charitable_deduction = tax_unit(
            "wa_millionaires_tax_charitable_deduction", period
        )
        standard_deduction = tax_unit("wa_millionaires_tax_standard_deduction", period)
        taxable_income = max_(
            base_income - charitable_deduction - standard_deduction, 0
        )
        return where(in_effect, taxable_income, 0)
