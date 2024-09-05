from policyengine_us.model_api import *


class ut_federal_deductions_for_taxpayer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah federal deductions considered for taxpayer credit"
    unit = USD
    documentation = "These federal deductions are added to the Utah personal exemption to determine the Utah taxpayer credit."
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        filing_status = tax_unit("filing_status", period)

        us_itemizing = tax_unit("tax_unit_itemizes", period)
        std_ded = tax_unit("standard_deduction", period)

        # Subtract SALT from Itemized Deductions
        deductions = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        item_ded = add(tax_unit, period, deductions)

        # Include Real Estate Taxes in Itemized Deductions
        real_estate_tax = add(tax_unit, period, ["real_estate_taxes"])

        capped_real_estate_tax = min_(
            real_estate_tax, p.itemized.salt_and_real_estate.cap[filing_status]
        )

        # Line 12. Federal Standard or Itemized Deductions
        total_item_ded = item_ded + capped_real_estate_tax
        return where(us_itemizing, total_item_ded, std_ded)
