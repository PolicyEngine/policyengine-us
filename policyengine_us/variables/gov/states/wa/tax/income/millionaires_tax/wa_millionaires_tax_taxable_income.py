from policyengine_us.model_api import *


class wa_millionaires_tax_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington millionaires tax taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=7",
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=13",
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=14",
    )
    defined_for = "wa_millionaires_tax_applies"

    def formula(tax_unit, period, parameters):
        base_income = tax_unit("wa_millionaires_tax_base_income", period)
        charitable_deduction = tax_unit(
            "wa_millionaires_tax_charitable_deduction", period
        )
        standard_deduction = tax_unit("wa_millionaires_tax_standard_deduction", period)
        return max_(base_income - charitable_deduction - standard_deduction, 0)
