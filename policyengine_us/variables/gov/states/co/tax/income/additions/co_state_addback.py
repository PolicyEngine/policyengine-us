from policyengine_us.model_api import *


class co_state_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado state income tax addback"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2021.pdf#page=5"
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5"
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        federal_itemizer = tax_unit("tax_unit_itemizes", period)
        state_inctax = max_(0, tax_unit("state_withheld_income_tax", period))
        property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        # follow worksheet on page 5 of 2021 Book cited above:
        irs_schA_line_5d = state_inctax + property_taxes
        irs_schA_line_5e = tax_unit("salt_deduction", period)
        ws_line_a = where(
            irs_schA_line_5d > irs_schA_line_5e,
            max_(0, irs_schA_line_5e - property_taxes),
            state_inctax,
        )
        p = parameters(period).gov.irs.deductions
        ws_line_b = add(tax_unit, period, p.itemized_deductions)
        ws_line_c = tax_unit("standard_deduction", period)
        ws_line_d = max_(0, ws_line_b - ws_line_c)
        return federal_itemizer * min_(ws_line_a, ws_line_d)
