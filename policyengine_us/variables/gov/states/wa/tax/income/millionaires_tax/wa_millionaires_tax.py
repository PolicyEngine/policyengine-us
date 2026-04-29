from policyengine_us.model_api import *


class wa_millionaires_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington millionaires tax"
    unit = USD
    definition_period = YEAR
    reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=7"
    defined_for = "wa_millionaires_tax_applies"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wa.tax.income.millionaires_tax
        taxable_income = tax_unit("wa_millionaires_tax_taxable_income", period)
        return taxable_income * p.rate
