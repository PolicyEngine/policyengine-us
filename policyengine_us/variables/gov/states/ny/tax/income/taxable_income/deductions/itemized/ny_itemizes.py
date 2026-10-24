from policyengine_us.model_api import *


class ny_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes New York deductions"
    documentation = "Whether the tax unit takes the New York itemized deduction, which it does when that is at least the New York standard deduction. Before 2018 only federal itemizers could itemize for New York."
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/613",
        "https://legislation.nysenate.gov/pdf/laws/TAX615",
        "https://www.tax.ny.gov/pdf/2017/inc/it201i_2017.pdf#page=20",
        "https://www.tax.ny.gov/pdf/2018/inc/it196i_2018.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.deductions.itemized
        may_itemize = True
        if p.federal_itemization_required:
            may_itemize = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("ny_standard_deduction", period)
        itemized_deductions = tax_unit("ny_itemized_deductions", period)
        return may_itemize & (itemized_deductions >= standard_deduction)
