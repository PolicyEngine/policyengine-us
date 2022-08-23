from openfisca_us.model_api import *


class md_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://govt.westlaw.com/mdc/Document/N05479690A64A11DBB5DDAC3692B918BC?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Check if the tax_unit itemized on their federal returns:
        tax_unit_itemizes = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("md_standard_deduction", period)
        gov = parameters(period).gov
        federal_deductions_if_itemizing = (
            gov.irs.deductions.deductions_if_itemizing
        )
        federal_deductions_if_itemizing = [
            deduction
            for deduction in federal_deductions_if_itemizing
            if deduction
            not in [
                "salt_deduction",
                "qualified_business_income_deduction",
            ]
        ]
        itemized_deductions_less_salt = add(
            tax_unit, period, federal_deductions_if_itemizing
        )
        return where(
            tax_unit_itemizes,
            itemized_deductions_less_salt,
            standard_deduction,
        )
