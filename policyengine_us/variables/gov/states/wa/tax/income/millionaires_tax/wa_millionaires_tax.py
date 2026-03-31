from policyengine_us.model_api import *


class wa_millionaires_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington millionaires tax"
    unit = USD
    definition_period = YEAR
    reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=6"
    defined_for = "wa_millionaires_tax_applies"
    documentation = """
    ESSB 6346 Sec. 201(1) imposes a tax of 9.9% on Washington taxable income,
    beginning January 1, 2028. The tax applies to Washington residents with
    taxable income above $1,000,000.

    This is sometimes referred to as the "millionaires tax" because the
    $1,000,000 standard deduction means only households with income above
    that threshold owe any tax.
    """

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wa.tax.income.millionaires_tax
        taxable_income = tax_unit("wa_millionaires_tax_taxable_income", period)
        return taxable_income * p.rate
