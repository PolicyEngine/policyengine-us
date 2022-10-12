from policyengine_us.model_api import *


class ny_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes NY deductions"
    unit = USD
    documentation = "Tax units who itemize their federal deductions can opt to itemize their NY deductions. However, if a standard deduction causes a lower tax liability, they must choose that."
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://www.nysenate.gov/legislation/laws/TAX/613"

    def formula(tax_unit, period, parameters):
        federal_itemizes = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("ny_standard_deduction", period)
        itemized_deductions = tax_unit("ny_itemized_deductions", period)
        return federal_itemizes & (itemized_deductions >= standard_deduction)
