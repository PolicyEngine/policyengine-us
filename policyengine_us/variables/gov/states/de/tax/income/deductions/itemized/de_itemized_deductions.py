from policyengine_us.model_api import *


class de_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/TY22_PIT-RSA_2022-02_PaperInteractive.pdf",  # § 1109
        "https://delcode.delaware.gov/title30/c011/sc02/index.html",
    )
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        filing_status = tax_unit("filing_status", period)
        deductions = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        federal_deductions = add(tax_unit, period, deductions)

        real_estate_tax = add(tax_unit, period, ["real_estate_taxes"])

        capped_real_estate_tax = min_(
            real_estate_tax, p.itemized.salt_and_real_estate.cap[filing_status]
        )

        return federal_deductions + capped_real_estate_tax
