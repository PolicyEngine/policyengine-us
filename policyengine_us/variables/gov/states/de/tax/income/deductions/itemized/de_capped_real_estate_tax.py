from policyengine_us.model_api import *


class de_capped_real_estate_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware capped real estate tax"
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
        real_estate_tax = add(tax_unit, period, ["real_estate_taxes"])
        cap = p.itemized.salt_and_real_estate.cap[filing_status]
        return min_(real_estate_tax, cap)
