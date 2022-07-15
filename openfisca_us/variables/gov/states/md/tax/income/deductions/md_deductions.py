from openfisca_us.model_api import *


class md_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://govt.westlaw.com/mdc/Document/N05479690A64A11DBB5DDAC3692B918BC?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)"

    def formula(tax_unit, period, parameters):
        # Check if the tax_unit itemized on their federal returns:
        tax_unit_itemizes = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("md_standard_deduction", period)
        federal_deductions_if_itemizing = tax_unit_itemizes * tax_unit(
            "taxable_income_deductions_if_itemizing", period
        )
        salt = tax_unit("salt_deduction", period)
        md_deductions = federal_deductions_if_itemizing - salt
        return where(tax_unit_itemizes, md_deductions, standard_deduction)
